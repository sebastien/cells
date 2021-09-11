from typing import Dict, OrderedDict, Any, Tuple
from ..kernel import BaseKernel
from ..utils import sig
import re

RE_INDENT = re.compile(r"^(\s*)(.*)$")


def splitIndent(line: str) -> Tuple[str, str]:
    """Splits each line as a (indent,rest) tuple. See `RE_INDENT`."""
    match = RE_INDENT.match(line)
    if not match:
        return ('', line)
    else:
        return (match.group(1) if match.group(1) else "", match.group(2) or "")


def untab(line: str) -> str:
    """Ensures the line starts with only spaces"""
    prefix, suffix = splitIndent(line)
    indent = prefix.replace("\t", "     ")
    return f"{indent}{suffix}"


class DynamicEnvironment(OrderedDict):

    def get(self, key):
        print("XXX", key)
        return super().get(key)

    def __keytransform__(self, key):
        print("TRAN", key)
        return key

    def __contains__(self, key: str) -> bool:
        print("HAS?", key)
        return super().__contains__(key)

    def __getitem__(self, k: str) -> Any:
        print("GETTING", k)
        return super().__getitem__(k)

    def __getattr__(self, k: str) -> Any:
        print("GETTING.A", k)
        return super().__getitem__(k)

    def __setitem__(self, k: str, v: Any) -> None:
        print("SETTING.K", k, v)
        return super().__setitem__(k, v)

    def __setattr__(self, k: str, v: Any) -> None:
        print("SETTING.A", k)
        return super().__setitem__(k, v)


# TODO: The slot invalidation should really be moved to the abstract kernel.


class PythonKernel(BaseKernel):

    def defineSlot(self, session: str, slot: str):
        s = self.getSlot(session, slot)
        assert s.type == "python", f"Type not supported: {s.type}"
        # TODO: We should make sure we can retab the input, as otherwise Python will complain about
        # mixed tabs and spaces
        slot_lines = [untab(f"\t{line}")
                      for line in (s.source or "").split("\n")]
        # FIXME: I'm not sure why we need that
        # ref = f"S{sig([session])}_{slot}"
        # slot_lines.insert(
        #     0, f"def {ref}({', '.join(s.inputs)}):")
        # while not slot_lines[-1].strip():
        #     slot_lines.pop()
        # if len(slot_lines) == 1:
        #     slot_lines.append(untab("\tpass"))
        # # NOTE: This means that the code must end with an expression
        # indent, result = splitIndent(slot_lines.pop())
        # slot_lines.append(f"{indent}{result}")
        # slot_code = "\n".join(slot_lines)
        slot_code = s.source

        # We evaluate the function in a completely standalone environment
        scope_locals: OrderedDict[str, Any] = OrderedDict()
        scope_globals: OrderedDict[str, Any] = OrderedDict()
        exec(slot_code, scope_globals, scope_locals)
        # NOTE: We should check that the scope only has one entry
        slot_def = None
        for v in scope_locals.values():
            slot_def = v
        # We update the slot definition
        s.definition = slot_def
        # FIXME: This is probably not right, the source
        # should probably be the cell/slot's original source, not
        # the one we synthesized.
        s.source = slot_code
        return s

    def evalSlot(self, session: str, slot: str):
        s = self.getSlot(session, slot)
        args = [self.get(session, _) for _ in s.inputs or ()]
        scope_locals: OrderedDict[str, Any] = DynamicEnvironment()
        assert s.definition, f"Slot '{session}.{slot}' has no definition: {s}"
        scope_globals: OrderedDict[str, Any] = DynamicEnvironment(
            _d=s.definition,
            _a=args,
        )
        exec("_d(*_a)", scope_globals, scope_locals)
        print("SLOT", slot, "DEFINES", [
              _ for _ in scope_locals], "uses", [_ for _ in scope_globals])
        return s.definition(*args) if s.definition else None

# EOF

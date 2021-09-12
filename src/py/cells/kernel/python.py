from typing import Dict, OrderedDict, Any, Tuple
from ..kernel import BaseKernel, Slot
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


# NOTE: Not sure this is really going to be necessary, but leaving it for
# now.
class DynamicEnvironment(OrderedDict):

    def get(self, key):
        return super().get(key)

    def __keytransform__(self, key):
        return key

    def __contains__(self, key: str) -> bool:
        return super().__contains__(key)

    def __getitem__(self, k: str) -> Any:
        return super().__getitem__(k)

    def __getattr__(self, k: str) -> Any:
        return super().__getitem__(k)

    def __setitem__(self, k: str, v: Any) -> None:
        return super().__setitem__(k, v)

    def __setattr__(self, k: str, v: Any) -> None:
        return super().__setitem__(k, v)


# TODO: The slot invalidation should really be moved to the abstract kernel.


class PythonKernel(BaseKernel):

    def defineSlot(self, session: str, slot: str):
        s: Slot = self.getSlot(session, slot)
        assert s.type == "python", f"Type not supported: {s.type}"
        # NOTE: Now that we kind of assume that cells are evaluable expressions,
        # this should work.
        # --
        # TODO: We should make sure we can retab the input, as otherwise Python will complain about
        # mixed tabs and spaces
        # slot_lines = [untab(f"\t{line}")
        #               for line in (s.source or "").split("\n")]
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

        # # We evaluate the function in a completely standalone environment
        # scope_locals: OrderedDict[str, Any] = OrderedDict()
        # scope_globals: OrderedDict[str, Any] = OrderedDict()
        # exec(slot_code, scope_globals, scope_locals)
        # # NOTE: We should check that the scope only has one entry
        # slot_def = None
        # for v in scope_locals.values():
        #     slot_def = v
        # We update the slot definition
        # s.definition = slot_def
        # FIXME: This is probably not right, the source
        # should probably be the cell/slot's original source, not
        # the one we synthesized.
        s.source = slot_code
        return s

    # TODO: The caching should be done at the generic kernel level
    def evalSlot(self, session: str, slot: str):
        """Returns the value of the given slot for the given session."""
        s: Slot = self.getSlot(session, slot)
        scope_locals: OrderedDict[str, Any] = DynamicEnvironment()
        scope_globals: OrderedDict[str, Any] = DynamicEnvironment()
        for input_name in (s.inputs or ()):
            input_slot = self.get(session, input_name)
            scope_globals[input_name] = True
        exec(s.source, scope_locals, scope_globals)
        return scope_globals[slot]

# EOF

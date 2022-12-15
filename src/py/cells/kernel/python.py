from typing import OrderedDict, Any, Optional, cast
from ..kernel import BaseKernel, Slot
from ..utils import sig
import re

RE_INDENT = re.compile(r"^(\s*)(.*)$")


def splitIndent(line: str) -> tuple[str, str]:
    """Splits each line as a (indent,rest) tuple. See `RE_INDENT`."""
    match = RE_INDENT.match(line)
    if not match:
        return ("", line)
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
    def __init__(self, defaults: Optional[dict[str, Any]] = None):
        super().__init__()
        for k, v in (defaults or {}).items():
            self[k] = v

    def get(self, key):
        return super().get(key)

    def __keytransform__(self, key):
        return key

    def __contains__(self, key: str) -> bool:
        return super().__contains__(key)

    def __getitem__(self, k: str) -> Any:
        if super().__contains__(k):
            return super().__getitem__(k)
        else:
            print("Does not contain", k)
            return None

    def __getattr__(self, k: str) -> Any:
        return super().__getitem__(k)

    def __setitem__(self, k: str, v: Any) -> None:
        return super().__setitem__(k, v)

    def __setattr__(self, k: str, v: Any) -> None:
        return super().__setitem__(k, v)


# TODO: The slot invalidation should really be moved to the abstract kernel.


def slotCode(source: str, inputs: list[str]) -> str:
    """Returns wrapped source code from the given slot source, when executing
    that source code, the `_` variable will be assigned with the result of the execution
    of the source code."""
    # TODO: We should make sure we can retab the input, as otherwise Python will complain about
    # mixed tabs and spaces
    name = "_Sl0t_R3zUlT_"
    slot_lines = [untab(f"\t{line}") for line in (source or "").split("\n")]
    # FIXME: I'm not sure why we need that
    slot_lines.insert(0, f"def {name}({', '.join(inputs)}):")
    while not slot_lines[-1].strip():
        slot_lines.pop()
    if len(slot_lines) == 1:
        slot_lines.append(untab("\tpass"))
    # NOTE: This means that the code must end with an expression
    indent, result = splitIndent(slot_lines.pop())
    slot_lines.append(f"{indent}return ({result})")
    slot_lines.append(f"_ = {name}({', '.join(_ for _ in inputs)})")
    return "\n".join(slot_lines)


def evalSlot(source: str, inputs: list[str], context: dict[str, Any]) -> Any:
    """Evaluates the given source code using the given inputs"""
    slot_code = slotCode(source, inputs)
    print("SLOT CODE", slot_code)
    exec(slot_code, context, slot_locals := cast(dict[str, Any], {}))
    return slot_locals["_"]


class PythonKernel(BaseKernel):
    def __init__(self):
        super().__init__()
        self.compiledSlots: dict[str, str] = {}

    def defineSlot(self, session: str, slot: Slot) -> Slot:
        assert slot.type == "python", f"Type not supported: {slot.type}"
        self.compiledSlots[slot.name] = slotCode(slot.source or "None", slot.inputs)
        self.sessionState.setdefault(session, {})
        return slot

    # TODO: The caching should be done at the generic kernel level
    def evalSlot(self, session: str, slot: Slot) -> Any:
        """Returns the value of the given slot for the given session."""
        assert isinstance(slot, Slot)
        slot_source = self.compiledSlots[slot.name]
        # NOTE: This makes unnecessary copies
        slot_context = {k: v[1] for k, v in self.sessionState[session].items()}
        exec(slot_source, slot_context, scope := cast(dict[str, Any], {}))
        res = scope["_"]
        return res


# EOF

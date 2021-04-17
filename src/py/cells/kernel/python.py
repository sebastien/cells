from typing import Dict, List, Any, Tuple
from ..kernel import BaseKernel, Slot
from ..utils import sig
import re
import time

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


# TODO: The slot invalidation should really be moved to the abstract kernel.
class PythonKernel(BaseKernel):

    def defineSlot(self, session: str, slot: str):
        s = self.getSlot(session, slot)
        assert s.type == "python", f"Type not supported: {s.type}"
        # TODO: We should make sure we can retab the input, as otherwise Python will complain about
        # mixed tabs and spaces
        slot_lines = [untab(f"\t{line}")
                      for line in (s.source or "").split("\n")]
        ref = f"S{sig([session])}_{slot}"
        slot_lines.insert(
            0, f"def {ref}({', '.join(s.inputs)}):")
        while not slot_lines[-1].strip():
            slot_lines.pop()
        # NOTE: This means that the code must end with an expression
        indent, result = splitIndent(slot_lines.pop())
        slot_lines.append(f"{indent}return {result}")
        slot_code = "\n".join(slot_lines)
        # We evaluate the function in a completely standalone environment
        scope: Dict[str, Any] = {}
        exec(slot_code, {}, scope)
        # NOTE: We should check that the scope only has one entry
        slot_def = scope[ref]
        # We update the slot
        s.definition = slot_def
        s.source = slot_code
        return s

    def evalSlot(self, session: str, slot: str):
        s = self.getSlot(session, slot)
        args = [self.get(session, _) for _ in s.inputs or ()]
        return s.definition(*args) if s.definition else None

# EOF

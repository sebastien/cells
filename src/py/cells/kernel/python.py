from typing import Dict, List, Any, Tuple
from ..kernel import IKernel, Slot, Session
from ..utils import sig
import re
import time

RE_INDENT = re.compile(r"^(\s*)(.*)$")


def splitindent(line: str) -> Tuple[str, str]:
    """Ensures the line starts with only spaces"""
    match = RE_INDENT.match(line)
    if not match:
        return ('', line)
    else:
        return (match.group(1) if match.group(1) else "", match.group(2) or "")


def untab(line: str) -> str:
    """Ensures the line starts with only spaces"""
    prefix, suffix = splitindent(line)
    indent = prefix.replace("\t", "     ")
    return f"{indent}{suffix}"


# TODO: The slot invalidation should really be moved to the abstract kernel.
class PythonKernel(IKernel):

    # TODO: Session metadata (created)

    def __init__(self):
        self.sessions: Dict[str, Session] = {}

    def session(self, session: str) -> Session:
        """Returns the session with the given name, creating it if necessary."""
        return self.sessions[session] if session in self.sessions else self.sessions.setdefault(
            session, Session(time.time(), {}))

    def slot(self, session: str, slot: str) -> Slot:
        """Returns the slot with the given name in the given session, creating it if necessary."""
        s = self.session(session)
        return s.slots[slot] if slot in s.slots else s.slots.setdefault(slot, Slot())

    def set(self, session: str, slot: str, inputs: List[str], source: str, type: str = "python"):
        assert type == "python", f"Type not supported: {type}"
        # TODO: We should make sure we can retab the input, as otherwise Python will complain about
        # mixed tabs and spaces
        slot_lines = [untab(f"\t{line}") for line in source.split("\n")]
        ref = f"S{sig([session])}_{slot}"
        slot_lines.insert(
            0, f"def {ref}({', '.join(inputs)}):")
        while not slot_lines[1].strip():
            slot_lines.pop()
        # NOTE: This means that the code must end with an expression
        indent, result = splitindent(slot_lines.pop())
        slot_lines.append(f"{indent}return {result}")
        slot_code = "\n".join(slot_lines)
        # We evaluate the function in a completely standalone environment
        scope: Dict[str, Any] = {}
        exec(slot_code, {}, scope)
        # NOTE: We should check that the scope only has one entry
        slot_def = scope[ref]
        # We update the slot
        s = self.slot(session, slot)
        # TODO: We could check if the inputs have changes
        s.inputs = [_ for _ in inputs]
        print(f"set: {session}.{slot}= {slot_code}")
        for n in self.session(session).dag.setInputs(slot, s.inputs).descendants(slot):
            print(f"    invalidate {n}")
            self.slot(session, n).isDirty = True
        s.definition = slot_def
        s.source = slot_code
        s.isDirty = True
        return True

    def get(self, session: str, slot: str):
        s = self.slot(session, slot)
        if s.isDirty:
            # NOTE: This will trigger a recursive loop if it's not a DAG
            args = [self.get(session, _) for _ in s.inputs]
            s.value = s.definition(*args) if s.definition else None
            s.isDirty = False
            print(f"get: {session}.{slot}= {s.value} ({s.inputs} → {args})")
        else:
            print(f"get: {session}.{slot}={s.value}[cached]")
        return s.value

# EOF
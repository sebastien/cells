from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import time


@dataclass
class Slot:
    type: Optional[str] = None
    inputs: List[str] = field(default_factory=list)
    source: Optional[str] = None
    value: Optional[Any] = None
    isDirty: bool = True
    definition: Any = None


@dataclass
class Session:
    timestamp: float
    slots: Dict[str, Slot] = field(default_factory=dict)


# NOTE: Design decision: the Kernel is "dump" and does not need to take care of the DAG. The
# client will implement that logic and direct what needs to be changed. This helps simplify the
# development of kernels and centralize the hard parts in the client.
class IKernel:

    def set(self, session: str, slot: str, inputs: List[str], source: str, type: str):
        """Sets the given slot to use the given inputs with the given source and type"""
        raise NotImplemented

    def get(self, session: str, slot: str):
        """Returns the value of the given slot."""
        raise NotImplemented

    def invalidate(self, session: str, slots: List[str]):
        """Invalidates the given slots, indicating that their value is out of date."""
        raise NotImplemented

    def getHTML(self, session: str, slot: str) -> str:
        """Returns the HTML representation of the given slot."""
        raise NotImplemented

    def getJSON(self, session: str, slot: str) -> str:
        """Returns the JSON representation of the given slot."""
        raise NotImplemented

    def update(self, session: str, cells: List[str]) -> str:
        """Triggers an update of the given cells, in the defined order."""
        raise NotImplemented


class BaseKernel(IKernel):

    def __init__(self):
        super().__init__()
        self.sessions: Dict[str, Session] = {}

    def getSession(self, session: str) -> Session:
        """Returns the session with the given name, creating it if necessary."""
        return self.sessions[session] if session in self.sessions else self.sessions.setdefault(
            session, Session(time.time(), {}))

    def hasSlot(self, session: str, slot: str) -> bool:
        return slot in self.sessions[session].slots if session in self.sessions else False

    def getSlot(self, session: str, slot: str) -> Slot:
        """Returns the slot with the given name in the given session, creating it if necessary."""
        s = self.getSession(session)
        return s.slots[slot] if slot in s.slots else s.slots.setdefault(slot, Slot())

    def set(self, session: str, slot: str, inputs: List[str], source: str, type: str) -> bool:
        # We update the slot
        s = self.getSlot(session, slot)
        # TODO: We could check if the inputs have changes
        s.type = type
        s.inputs = [_ for _ in inputs]
        s.source = source
        s.isDirty = True
        self.defineSlot(session, slot)
        return True

    def get(self, session: str, slot: str):
        if not self.hasSlot(session, slot):
            raise ValueError(f"Undefined slot: '{session}.{slot}'")
        s = self.getSlot(session, slot)
        if s.isDirty:
            # NOTE: This will trigger a recursive loop if it's not a DAG
            s.value = self.evalSlot(session, slot)
            s.isDirty = False
        return s.value

    def invalidate(self, session: str, slots: List[str]) -> bool:
        for slot in slots:
            self.getSlot(session, slot).isDirty = True
        return True

    def defineSlot(self, session: str, slot: str):
        raise NotImplementedError

    def evalSlot(self, session: str, slot: str):
        raise NotImplementedError

# NOTE: We should do a stack Kernel | (HTTP|JSONRPC) | (Pipe|Socket)


class JSONRPCAdapter:

    def __init__(self, kernel: IKernel):
        self.kernel = kernel

    async def handle(self, request: dict) -> dict:
        # EX: {"jsonrpc": "2.0", "method": "subtract", "params": {"minuend": 42, "subtrahend": 23}, "id": 3}
        protocol = request.get("jsonrpc")
        method = request.get("method")
        rid = request.get("id")
        params = request.get("params", {})
        f = getattr(self.kernel, "method")
        res = f(**params)
        return res


# class AIOPipeServer:
#
#     def __init__(self, in =sys.stdin, out=sys.stdout):
#         self
#
#      def run( self ):
#          pass

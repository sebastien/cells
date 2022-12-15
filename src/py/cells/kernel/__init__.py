from dataclasses import dataclass, field
from typing import Optional, Any, cast
from enum import Enum
import time
import os
import inspect
import importlib


@dataclass
class Slot:
    name: str
    type: Optional[str] = None
    inputs: tuple[str, ...] = ()
    source: Optional[str] = None
    revision: int = 0
    definition: Any = None


@dataclass
class Session:
    timestamp: float
    slots: dict[str, Slot] = field(default_factory=dict)


class RenderFormat(Enum):
    HTML = "html"
    Text = "text"
    JSON = "json"


# NOTE: Design decision: the Kernel is "dump" and does not need to take care of the DAG. The
# client will implement that logic and direct what needs to be changed. This helps simplify the
# development of kernels and centralize the hard parts in the client.


class IKernel:

    # TODO: Must define the BaseKernel interface
    def set(self, session: str, slot: str, inputs: list[str], source: str, type: str):
        """Sets the given slot to use the given inputs with the given source and type"""
        raise NotImplemented

    def get(self, session: str, slot: str) -> Any:
        """Returns the value of the given slot."""
        raise NotImplemented

    def invalidate(self, session: str, slots: list[str]):
        """Invalidates the given slots, indicating that their value is out of date."""
        raise NotImplemented

    def getHTML(self, session: str, slot: str) -> str:
        """Returns the HTML representation of the given slot."""
        raise NotImplemented

    def getJSON(self, session: str, slot: str) -> str:
        """Returns the JSON representation of the given slot."""
        raise NotImplemented

    def update(self, session: str, cells: list[str]) -> str:
        """Triggers an update of the given cells, in the defined order."""
        raise NotImplemented

    def render(self, session: str, slot: str, format: RenderFormat) -> str:
        """Renders the result of the given slot and returns an HTML string"""
        raise NotImplementedError


class BaseKernel(IKernel):
    def __init__(self):
        super().__init__()
        self.sessions: dict[str, Session] = {}
        self.sessionState: dict[str, dict[str, tuple[int, Any]]] = {}

    def set(
        self, session: str, slot: str, inputs: tuple[str, ...], source: str, type: str
    ) -> bool:
        # We update the slot
        s = self.getSlot(session, slot)
        # TODO: We could check if the inputs have changes
        s.type = type
        s.inputs = inputs
        s.source = source
        s.revision += 1
        self.defineSlot(session, s)
        return True

    def get(self, session: str, slot: str) -> Any:
        if not self.hasSlot(session, slot):
            raise ValueError(f"Undefined slot: '{session}.{slot}'")
        s = self.getSlot(session, slot)
        r, v = self.sessionState.get(session, {}).get(slot, (None, None))
        if r != s.revision:
            # NOTE: This will trigger a recursive loop if it's not a DAG
            w = self.evalSlot(session, s)
            self.sessionState.setdefault(session, {})[slot] = (s.revision, w)
            return w
        else:
            return v

    def invalidate(self, session: str, slots: list[str]) -> bool:
        if session in self.sessionState:
            s = self.sessionState[session]
            for slot in slots:
                del s[slot]
        return True

    def getSession(self, session: str) -> Session:
        """Returns the session with the given name, creating it if necessary."""
        return (
            self.sessions[session]
            if session in self.sessions
            else self.sessions.setdefault(session, Session(time.time(), {}))
        )

    def hasSlot(self, session: str, slot: str) -> bool:
        return (
            slot in self.sessions[session].slots if session in self.sessions else False
        )

    def getSlot(self, session: str, slot: str) -> Slot:
        """Returns the slot with the given name in the given session, creating it if necessary."""
        s = self.getSession(session)
        assert self.sessions[session] is s
        return (
            s.slots[slot]
            if slot in s.slots
            else s.slots.setdefault(slot, Slot(name=slot))
        )

    def defineSlot(self, session: str, slot: Slot):
        raise NotImplementedError

    def evalSlot(self, session: str, slot: Slot):
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


class AIOPipeServer:
    pass
    #
    #     def __init__(self, in =sys.stdin, out=sys.stdout):
    #         self
    #
    #      def run( self ):
    #          pass


# --
# ## Kernel Discovery
#
# We introspect the `cells.kernel` module and retrieves a dict of languages
# to kernel classes.

KERNELS = [
    _.split(".")[0]
    for _ in os.listdir(os.path.dirname(os.path.abspath(__file__)))
    if _.endswith(".py") and not _.startswith("_")
]


def loadKernels() -> dict[str, IKernel]:
    """Loads the kernel submodules"""
    return dict((k, v) for k, v in ((_, loadKernel(_)) for _ in KERNELS) if v)


def loadKernel(name: str) -> Optional[IKernel]:
    module = importlib.import_module(f"cells.kernel.{name}")
    for key in dir(module):
        value = getattr(module, key)
        if inspect.isclass(value) and issubclass(value, IKernel):
            return cast(IKernel, value)
    return None


# EOF

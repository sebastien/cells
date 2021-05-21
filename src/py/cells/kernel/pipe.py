from ..kernel import IKernel, BaseKernel, Slot
from typing import Dict, List, Optional


class PipeKernel(BaseKernel):
    """A kernel that is interacted with using an ASCII protocol using `in` and `out`
    channels."""

    def __init__(self, kernels: Dict[str, IKernel]):
        super().__init__()
        self.kernels: Dict[str, IKernel] = {}
        self.slots: Dict[str, str] = {}
        for k, v in kernels.items():
            for _ in k.split("|"):
                assert _ not in self.kernels, f"Duplicate kernel entry for type: {_}, {self.kernels[_]} != {v}"
                self.kernels[_] = v

    def getKernel(self, type: Optional[str]) -> IKernel:
        """Returns the kernel for the given type, or throws an exception if 
        not there."""
        assert type, "Cannot retrieve a kernel without a type"
        if not type in self.kernels:
            raise ValueError(f"No kernel registered for type: {type}")
        return self.kernels[type]

    def set(self, session: str, slot: str, inputs: List[str], source: str, type: str) -> Slot:
        s = super().set(session, slot, inputs, source, type)
        kernel = self.getKernel(type)
        return kernel.set(session, slot, inputs, source, type)
        # TODO
        # if not s.type:
        #     # New slot
        #     s.type = type
        #     pass
        # elif s.type == type:
        #     # Same slot
        #     pass
        # else:
        #     # Different slot
        #     s.type = type

    def get(self, session: str, slot: str):
        s = self.getSlot(session, slot)
        assert s.type, f"Slot has no type: {session}.{slot}"
        kernel = self.getKernel(s.type)
        return kernel.get(session, slot)

    def invalidate(self, session: str, slots: List[str]) -> bool:
        for slot in slots:
            s = self.getSlot(session, slot)
            s.isDirty = True
            kernel = self.getKernel(s.type)
            kernel.invalidate(session, slots)
        return True

    def defineSlot(self, session: str, slot: str):
        pass


class PipedProcessKernel(PipeKernel):
    """A piped kernel that is run through a process"""

# EOF

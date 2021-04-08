from typing import Iterable, Any, Optional, List, Dict
import hashlib


def sig(content: List[str]) -> bytes:
    h = hashlib.sha3_256()
    for _ in content:
        h.update(bytes(_, "utf8"))
    return h.digest()


class Cell:
    """Cells wrap an evaluable representation. The evaluation of the representation
    can be done in a language-specific kernel and a corresponding context, which
    contains value.
    """
    IDS: int = 0

    def __init__(self, name: Optional[str] = None, type: Optional[str] = None, deps: Optional[List[str]] = None):
        self.id = str(Cell.IDS)
        Cell.IDS += 1
        self.name: Optional[str] = name
        self.type = type
        self.inputs: List[str] = [_ for _ in deps or ()]
        self._content: List[str] = []
        self.value: Any = None

    @property
    def ref(self) -> str:
        return self.name or self.id

    @property
    def inputsSignature(self) -> bytes:
        return sig(self.inputs)

    @property
    def contentSignature(self) -> bytes:
        return sig(self._content)

    @property
    def content(self) -> str:
        lines = self._content
        i = len(lines) - 1
        while i >= 0 and lines[i].strip() == "\n":
            i -= 1
        return "".join(lines[:i+1])

    def add(self, line: str) -> str:
        self._content.append(line)
        return line

    def iterSource(self) -> Iterable[str]:
        is_empty = not (self.name or self.type or self.inputs)
        yield "--" if is_empty else "-- "
        if self.name:
            yield self.name
        if self.type:
            yield f":{self.type}"
        if self.inputs:
            yield f" < {' '.join(self.inputs)}"
        yield "\n"
        for _ in self._content:
            yield _

    def toSource(self) -> str:
        return "".join(_ for _ in self.iterSource())

    def toPrimitive(self):
        return dict((k, v) for k, v in {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "inputs": self.inputs,
            "content": self.content,
        }.items() if v is not None and v != [])


class Document:
    """A block contains a list of cells and is able to perform operations on them."""

    def __init__(self):
        self.cells: List[Cell] = []
        self._symbols: Dict[str, Cell] = {}

    def add(self, cell: Cell) -> Cell:
        assert cell not in self.cells, f"Cell added twice in {self}: {cell}"
        self.cells.append(cell)
        return cell

    def iterSource(self) -> Iterable[str]:
        for c in self.cells:
            yield from c.iterSource()

    def toSource(self) -> str:
        return "".join(_ for _ in self.iterSource())

    def toPrimitive(self):
        return [_.toPrimitive() for _ in self.cells]

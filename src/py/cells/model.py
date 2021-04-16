from typing import Iterable, Any, Optional, List, Dict
from .utils import sig, equal_lines
from .dag import DAG


class Cell:
    """Cells wrap an evaluable representation. The evaluation of the representation
    can be done in a language-specific kernel and a corresponding context, which
    contains value.
    """
    IDS: int = 0

    def __init__(self, name: Optional[str] = None, type: Optional[str] = None, inputs: Optional[List[str]] = None, content: str = ""):
        self.id = str(Cell.IDS)
        Cell.IDS += 1
        self.name: Optional[str] = name
        self.type = type
        self.inputs: List[str] = [_ for _ in inputs or ()]
        self._content: List[str] = content.split("\n")

    def equals(self, cell: 'Cell') -> bool:
        """Tells if this cell equals the other cell. This only checks
        type, inputs and content"""
        return self.type == cell.type and equal_lines(self.inputs, cell.inputs) and equal_lines(self._content, content)

    @property
    def ref(self) -> str:
        return self.name or self.id

    @property
    def inputsSignature(self) -> str:
        return sig(self.inputs)

    @property
    def contentSignature(self) -> str:
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
        self.dag: DAG = DAG()

    def prepare(self):
        self.dag.reset()
        for cell in self.cells:
            self.dag.setNode(cell.ref, cell.id)
            self.dag.addInputs(cell.ref, cell.inputs)
        return self

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

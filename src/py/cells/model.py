from typing import Iterable, Any, Optional, List, Dict
from .utils import sig, equal_lines
from .dag import DAG
import re

RE_EMPTY = re.compile("^\s*$")

# TODO: Striplies should be an option in the iteration of sources. Should probably
# also be moved to `utils`.


def striplines(lines: Iterable[str]) -> Iterable[str]:
    lines = [_ for _ in lines]
    n = len(lines)
    i = 0
    j = n - 1
    while i < n and not lines[i].strip():
        i += 1
    while j >= 0 and not lines[j].strip():
        j -= 1
    return lines[i:j+1]


class Cell:
    """Cells wrap an evaluable representation. The evaluation of the representation
    can be done in a language-specific kernel and a corresponding context, which
    contains value.
    """
    IDS: int = 0

    def __init__(self, name: Optional[str] = None, type: Optional[str] = None, inputs: Optional[List[str]] = None, modifiers: Optional[List[str]] = None, content: str = ""):
        self.id = str(Cell.IDS)
        Cell.IDS += 1
        self.name: Optional[str] = name
        self.type = type
        self.inputs: List[str] = [_ for _ in inputs or ()]
        self.modifiers: List[str] = [_ for _ in modifiers or ()]
        self._content: List[str] = content.split("\n")

    def equals(self, cell: 'Cell') -> bool:
        """Tells if this cell equals the other cell. This only checks
        type, inputs and content"""
        return self.type == cell.type and equal_lines(self.inputs, cell.inputs) and equal_lines(self._content, cell._content)

    @property
    def isEmpty(self) -> bool:
        for _ in self._content:
            if _ and not RE_EMPTY.match(_):
                return False
        return True

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
    def source(self) -> str:
        lines = self._content
        i = len(lines) - 1
        while i >= 0 and lines[i].strip() == "\n":
            i -= 1
        return "".join(lines[:i+1])

    @property
    def header(self) -> str:
        """Returns the one-liner cell header, in text format"""
        if not (self.name or self.type or self.inputs):
            return "--"
        res = ["-- "]
        if self.name:
            res.append(self.name)
        if self.type:
            res.append(f":{self.type}")
        if self.inputs:
            res.append(f" < {' '.join(self.inputs)}")
        return "".join(res)

    def add(self, line: str) -> str:
        self._content.append(line)
        return line

    def iterSource(self) -> Iterable[str]:
        yield self.header
        yield "\n"
        for _ in striplines(self._content):
            yield _

    def iterMarkdown(self) -> Iterable[str]:
        if self.type in ("md", None):
            for _ in self._content:
                yield _
        else:
            yield f"\n```{self.type}{' ' + self.header.strip() if self.name or self.inputs else ''}\n"
            for _ in (striplines(self._content)):
                yield _
            yield "```\n"

    def toSource(self) -> str:
        return "".join(_ for _ in self.iterSource())

    def toMarkdown(self) -> str:
        return "".join(_ for _ in self.iterMarkdown())

    def toPrimitive(self):
        return dict((k, v) for k, v in {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "inputs": self.inputs,
            "content": self._content,
        }.items() if v is not None and v != [])


class Document:
    """A block contains a list of cells and is able to perform operations on them."""

    def __init__(self):
        self.cells: List[Cell] = []
        self._symbols: Dict[str, Cell] = {}
        self.dag: DAG[Cell] = DAG()

    def prepare(self):
        self.dag.reset()
        for cell in self.cells:
            self.dag.setNode(cell.ref, cell)
            self.dag.addInputs(cell.ref, cell.inputs)
        return self

    def add(self, cell: Cell) -> Cell:
        assert cell not in self.cells, f"Cell added twice in {self}: {cell}"
        self.cells.append(cell)
        return cell

    def iterCells(self) -> Iterable[Cell]:
        """Iterates over the cells in growing rank order"""
        for _ in self.dag.ranks():
            cell = self.dag.getNode(_)
            if cell:
                yield cell

    def iterSource(self) -> Iterable[str]:
        for i, c in enumerate(_ for _ in self.cells if not _.isEmpty):
            if i != 0:
                yield "\n"
            yield from c.iterSource()

    def iterMarkdown(self) -> Iterable[str]:
        for i, c in enumerate(_ for _ in self.cells if not _.isEmpty):
            if i != 0:
                yield "\n"
            yield from c.iterMarkdown()

    def toSource(self) -> str:
        return "".join(_ for _ in self.iterSource())

    def toPrimitive(self):
        return [_.toPrimitive() for _ in self.cells]

    def __iter__(self) -> Iterable[Cell]:
        yield from self.iterCells()
# EOF

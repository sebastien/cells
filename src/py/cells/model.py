from typing import Iterable, Optional, Union, NamedTuple
from .utils import sig, equal_lines
from .dag import DAG
from dataclasses import dataclass
from pathlib import Path
import re

RE_EMPTY = re.compile("^\s*$")

# TODO: Striplines should be an option in the iteration of sources. Should probably
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


class Content:

    def __init__(self, source: str, start: int = 0, end: Optional[int] = None):
        self._source: str = source
        self.start: int = start
        self.end: int = len(source) if end is None else end
        self._lines: list[str] = source[start:end].split("\n")
        self.hasChanged: bool = False

    @property
    def range(self) -> tuple[int, int]:
        return (self.start, self.end)

    @property
    def lines(self) -> list[str]:
        return self._lines

    def append(self, line: str):
        self._lines.append(line)
        self.hasChanged = True
        return self

    def __equals__(self, value):
        return equal_lines(self.lines, value.lines) if isinstance(value, Content) else False

    def __str__(self) -> str:
        return "\n".join(self.lines)


class Cell:
    """Cells wrap an evaluable representation. The evaluation of the representation
    can be done in a language-specific kernel and a corresponding context, which
    contains value.
    """
    IDS: int = 0

    def __init__(self, name: Optional[str] = None, type: Optional[str] = None, inputs: Optional[list[str]] = None, modifiers: Optional[list[str]] = None, content: Union[str, tuple[str, int, int]] = ""):
        self.id = str(Cell.IDS)
        Cell.IDS += 1
        self.name: Optional[str] = name
        self.type = type
        self.inputs: list[str] = [_ for _ in inputs or ()]
        self.modifiers: list[str] = [_ for _ in modifiers or ()]
        self._content: Content = Content(content) if isinstance(
            content, str) else Content(content[0], content[1], content[2])

    def equals(self, cell: 'Cell') -> bool:
        """Tells if this cell equals the other cell. This only checks
        type, inputs and content"""
        return self.type == cell.type and equal_lines(self.inputs, cell.inputs) and self._content == cell._content

    @property
    def isEmpty(self) -> bool:
        for _ in self._content.lines:
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
        return sig(self._content.lines)

    @property
    def source(self) -> str:
        """Returns the source code for the cell as a string"""
        lines = self._content.lines
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
        for _ in striplines(self._content.lines):
            yield _

    def iterMarkdown(self) -> Iterable[str]:
        if self.type in ("md", None):
            for _ in self._content.lines:
                yield _
        else:
            yield f"\n```{self.type}{' ' + self.header.strip() if self.name or self.inputs else ''}\n"
            for _ in (striplines(self._content.lines)):
                yield _
            yield "```\n"

    def toSource(self) -> str:
        return "".join(_ for _ in self.iterSource())

    def toMarkdown(self) -> str:
        return "".join(_ for _ in self.iterMarkdown())

    def asDict(self):
        return dict((k, v) for k, v in {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "inputs": self.inputs,
            "range": self._content.range,
            "lines": self._content.lines,
        }.items() if v is not None and v != [])


class Document:
    """A block contains a list of cells and is able to perform operations on them."""

    def __init__(self):
        self.cells: list[Cell] = []
        self._symbols: dict[str, Cell] = {}
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

    def asDict(self):
        return [_.asDict() for _ in self.cells]

    def __iter__(self) -> Iterable[Cell]:
        yield from self.iterCells()
# EOF

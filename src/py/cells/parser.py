from typing import Iterable, Any, Optional, List, Tuple, Dict
import re

T_CONTENT = '='
T_COMMENT = "#"
T_DECLARATION = "+"
RE_COMMENT = re.compile(r"\s*#[ ]?(?P<value>.*)$")
RE_DEFINITION = re.compile(
    r"\s*(?P<name>[@\w_][\w_-]*)?(:(?P<type>\w+))?(\s*=(?P<value>.+))?\s*(\<\s*(?P<deps>[\w_]+(\s+[\w_]+)*))?$")


def idem(_): return _


class Cell:
    """Cells wrap an evaluable representation. The evaluation of the representation
    can be done in a kernel and using a context."""

    def __init__(self, name: Optional[str] = None, type: Optional[str] = None, deps: Optional[List[str]] = None):
        self.id = None
        self.name: Optional[str] = name
        self.type = type
        self._inputs: List[str] = [] + (deps or [])
        self.source: List[str] = []
        self.value: Any = None

    def add(self, line: str):
        self.source.append(line)
        return self


class Document:
    """A block contains a list of cells and is able to perform operations on them."""

    def __init__(self):
        self.cells: List[Cell] = []
        self._symbols: Dict[str, Cell] = {}

    def add(self, cell: Cell):
        assert cell not in self.cells, f"Cell added twice in {self}: {cell}"
        self.cells.append(cell)
        return self


class Parser:
    """Parses a Document and creates its Cells. The parser has an intermediate
    expanded line-by-line representation that can be used to generate an alternative model,
    like SAX and DOM for XML."""

    PROCESSOR = {
        "deps": lambda v: [_.strip() for _ in v.split()] if v else None
    }

    def __init__(self):
        self.start()

    def parseLine(self, line: str) -> Tuple[str, Any]:
        """Parses a line, returning a tuple prefixed by the parsed type. See
        `T_CONTENT`, `T_COMMENT` and `T_DEFINITION`."""
        if line.startswith("--"):
            return self.parseDefinition(line[2:].strip())
        else:
            return (T_CONTENT, line)

    def parseDefinition(self, line: str) -> Tuple[str, Any]:
        """Parses a definition line, starting with  `--`"""
        if match := RE_COMMENT.match(line):
            return (T_COMMENT, match.group("value"))
        elif match := RE_DEFINITION.match(line):
            return (T_DECLARATION, dict((k, v) for k, v in ((_, self.PROCESSOR.get(_, idem)(match.group(_))) for _ in ("name", "type", "value", "deps")) if v))
        else:
            raise SyntaxError(f"Could not parse: {line}")

    def start(self):
        self.document: Document = Document()
        self.cell: Optional[cell] = None
        return self

    def process(self, parsed: Tuple[str, Any]):
        type, data = parsed
        if type == T_DECLARATION:
            self.cell = self.document.add(Cell(**data))
        elif type == T_CONTENT:
            if not self.cell:
                self.cell = this.document.add(Cell())
            self.cell.add(data)


# EOF

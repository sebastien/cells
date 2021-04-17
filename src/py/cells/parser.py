from typing import Any, Optional, NamedTuple, Union
from .model import Cell, Document
from pathlib import Path
import re

RE_COMMENT = re.compile(r"\s*#[ ]?(?P<value>.*)$")
NAME = r'("[^"]+"|[@\w_][\w_-]*)'
RE_DEFINITION = re.compile("".join([
    r"\s*(?P<name>", NAME, r")?",
    r"(:(?P<type>\w+))?",
    r"(\s*=(?P<content>.+))?",
    r"\s*(\<\s*(?P<inputs>", NAME, r"(\s+", NAME, r")*))?\s*$"
]))


def idem(_):
    """Returns the value as-is"""
    return _


def unquote(text: str, quotes='"') -> str:
    """Unquotes the string"""
    return text[1:-1] if text and text[0] == text[-1] and text[0] in quotes else text


T_CONTENT = '='
T_COMMENT = "#"
T_DECLARATION = "+"

# These are the different types of parsed events


class ParseEvent(NamedTuple):
    """Simple abstraction over a parsed line, providing a SAX-like interface"""
    type: str
    value: Any


class Parser:
    """Parses a Document and creates its Cells. The parser has an intermediate
    expanded line-by-line representation that can be used to generate an alternative model,
    like SAX and DOM for XML."""

    PROCESSOR = {
        "inputs": lambda v: [unquote(_.strip()) for _ in v.split()] if v else None,
        "name": lambda _: unquote(_.strip()) if _ else None,
    }

    def __init__(self):
        self.start()

    def parse(self, source: Union[str, Path]):
        if isinstance(source, Path):
            with open(source) as f:
                for line in f.readlines():
                    self.feed(line)
        elif isinstance(source, str):
            for line in source.split("\n"):
                self.feed(line + "\n")
        else:
            raise ValueError(f"Unknown source type: {source}")
        return self

    def feed(self, line: str):
        self.processEvent(self.parseLine(line))
        return self

    def parseLine(self, line: str) -> ParseEvent:
        """Parses a line, returning a tuple prefixed by the parsed type. See
        `T_CONTENT`, `T_COMMENT` and `T_DEFINITION`."""
        if line.startswith("--"):
            return self.parseDefinition(line[2:].strip())
        else:
            return ParseEvent(T_CONTENT, line)

    def parseDefinition(self, line: str) -> ParseEvent:
        """Parses a definition line, starting with  `--`"""
        if match := RE_COMMENT.match(line):
            return ParseEvent(T_COMMENT, match.group("value"))
        elif match := RE_DEFINITION.match(line):
            return ParseEvent(T_DECLARATION, dict((k, v) for k, v in ((_, self.PROCESSOR.get(_, idem)(match.group(_))) for _ in ("name", "type", "content", "inputs")) if v))
        else:
            raise SyntaxError(f"Could not parse: {line}")

    def processEvent(self, parsed: ParseEvent):
        type, data = parsed
        if type == T_DECLARATION:
            self.cell = self.document.add(Cell(**data))
        elif type == T_CONTENT:
            if not self.cell:
                self.cell = self.document.add(Cell())
            self.cell.add(data)
        else:
            # It's a comment so we can safely skip it
            pass

    def start(self):
        self.document: Document = Document()
        self.cell: Optional[Cell] = None
        return self

    def end(self):
        return self.document.prepare()


def parse(*sources: Union[Path]):
    parser = Parser()
    for _ in sources:
        parser.parse(_)
    return parser.end()

# EOF

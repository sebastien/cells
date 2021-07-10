from typing import Any, Optional, NamedTuple, Union, Iterable
from .model import Cell, Document
from pathlib import Path
import re

RE_COMMENT = re.compile(r"\s*#[ ]?(?P<value>.*)$")
NAME = r'("[^"]+"|[@\w_][\w_-]*)'
RE_DEFINITION = re.compile("".join([
    r"\s*(?P<name>", NAME, r")?",
    r"(:(?P<type>\w+))?",
    r"(\s*\[(?P<modifiers>[\w\d\-_]+(\s+[\w\d\-_]+)*)\])?",
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


class IParser:

    def parse(self, source: Union[str, Path]):
        if isinstance(source, Path):
            with open(source) as f:
                self.parseLines(f.readlines())
        elif isinstance(source, str):
            self.parseLines(source.split("\n"))
        else:
            raise ValueError(f"Unknown source type: {source}")
        return self

    def parseLines(self, lines: Iterable[str]):
        raise NotImplementedError


class Parser(IParser):
    """Parses a Document and creates its Cells. The parser has an intermediate
    expanded line-by-line representation that can be used to generate an alternative model,
    like SAX and DOM for XML."""

    PROCESSOR = {
        "inputs": lambda v: [unquote(_.strip()) for _ in v.split()] if v else None,
        "modifiers": lambda v: [_.strip() for _ in v.split()] if v else None,
        "name": lambda _: unquote(_.strip()) if _ else None,
    }

    def __init__(self):
        self.start()

    def parseLines(self, lines: Iterable[str]):
        for _ in lines:
            self.parseLine(_)
        return self

    def parseLine(self, line: str) -> ParseEvent:
        """Parses a line, returning a tuple prefixed by the parsed type. See
        `T_CONTENT`, `T_COMMENT` and `T_DEFINITION`."""
        event = self.parseDefinition(line[2:].strip()) if line.startswith(
            "--") else ParseEvent(T_CONTENT, line)
        self.processEvent(event)
        return event

    def parseDefinition(self, line: str) -> ParseEvent:
        """Parses a definition line, starting with  `--`"""
        if match := RE_COMMENT.match(line):
            return ParseEvent(T_COMMENT, match.group("value"))
        elif match := RE_DEFINITION.match(line):
            return ParseEvent(T_DECLARATION, dict((k, v) for k, v in ((_, self.PROCESSOR.get(_, idem)(match.group(_))) for _ in ("name", "type", "content", "inputs", "modifiers")) if v))
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


class EmbeddedParser(IParser):

    RE_HASH_LINE = re.compile(r"^#( (?P<rest>.*)|\s*)$")
    RE_SLASH_LINE = re.compile(r"^//( (?P<rest>.*)|\s*)$")

    LANG = {
        "python": RE_HASH_LINE,
        "javascript": RE_SLASH_LINE,
    }

    @staticmethod
    def ExtractLines(lines: Iterable[str], lang="python"):
        """Extract cells definitions embedded in the commands of another language. This
        currrenlyt only works for comments that have the same prefix for each line, ie
        not `/*…*/`."""
        prefix = EmbeddedParser.LANG[lang]
        # FIXME: Not sure about the indentation prefix
        last_line_type = None
        for i, line in enumerate(lines):
            if match := prefix.match(line):
                rest = match.group("rest")
                if rest and (stripped := rest.lstrip()) and stripped.startswith("--"):
                    yield rest
                    last_line_type = "cell"
                    yield "\n"
                elif last_line_type == "cell":
                    yield rest or ""
                    yield "\n"
                else:
                    yield line
            elif last_line_type == "cell":
                last_line_type = None
                yield f"-- :{lang}"
                yield line
            elif i == 0:
                yield f"-- :{lang}"
                yield line
            else:
                yield line

    def __init__(self, parser: Parser = Parser()):
        self.parser = parser
        self.lang = "python"

    def parse(self, path: Path, lang: str):
        self.lang = lang
        return super().parse(path)

    def parseLines(self, lines: Iterable[str]):
        return self.parser.parseLines(
            EmbeddedParser.ExtractLines(lines, lang=self.lang))


LANGUAGES = {
    "python": [".py"],
    "javascript": [".js", ".jsx", ".ts"],
    "*": [],
}


def parse(*sources: Union[Path]):
    parser = Parser()
    embedded = EmbeddedParser(parser)
    for path in sources:
        ext = path.suffix
        # NOTE: This is where we can add extensibility to the language
        # matching.
        for lang, exts in LANGUAGES.items():
            if ext in exts:
                embedded.parse(path, lang)
                break
            elif not exts:
                parser.parse(path)
    return parser.end()

# EOF

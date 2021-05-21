import re
import sys
from pathlib import Path
from typing import Iterable
from . import Command
from ..parser import Parser


# TODO: Move to parser
def extractLines(lines: Iterable[str], lang, prefix=re.compile(r"^#( (?P<rest>.*)|\s*)$")):
    """Extract cells definitions embedded in the commands of another language. This
    currrenlyt only works for comments that have the same prefix for each line, ie
    not `/*…*/`."""
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


class FMT(Command):

    NAME = "fmt"
    HELP = "Formats the document"

    FORMATS = ["cd", "html", "md"]

    def define(self, parser):
        super().define(parser)
        parser.add_argument("-t", "--to", dest="format", action="store", default="cells",
                            help=f"Output format: {', '.join(self.FORMATS)}")
        parser.add_argument("files", metavar="FILE", type=str, nargs='*',
                            help='Input files to format')

    def run(self, args):
        parser = Parser()
        for path in (Path(_) for _ in args.files):
            ext = path.suffix
            if ext == ".py":
                with open(path) as f:
                    for line in extractLines((_ for _ in f.readlines()), "python"):
                        parser.feed(line)
            else:
                # It's a cells document
                parser.parse(Path(path))
        doc = parser.end()
        out = sys.stdout
        if args.format == "md":
            for chunk in doc.iterMarkdown():
                out.write(chunk)
        else:
            for chunk in doc.iterSource():
                out.write(chunk)
        # sys.stdout.write(doc.toSource())
        # sys.stdout.write(doc.toSource())

# EOF

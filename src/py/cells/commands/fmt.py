import re
import sys
from pathlib import Path
from . import Command
from ..parser import parse


class FMT(Command):

    NAME = "fmt"
    HELP = "Formats the document"

    FORMATS = ["cd", "html", "md"]

    def define(self, parser):
        super().define(parser)
        parser.add_argument("-t", "--to", dest="format", action="store", default="cells",
                            help=f"Output format: {', '.join(self.FORMATS)}")
        parser.add_argument("-o", "--output", dest="output", action="store", default="-",
                            help=f"Output file")
        parser.add_argument("files", metavar="FILE", type=str, nargs='*',
                            help='Input files to format')

    def run(self, args):
        doc = parse(*(Path(_) for _ in args.files))
        if args.output == "-":
            out = sys.stdout
        else:
            out = open(args.output, "w")
        if args.format == "md":
            for chunk in doc.iterMarkdown():
                out.write(chunk)
        else:
            for chunk in doc.iterSource():
                out.write(chunk)
        if out != sys.stdout:
            out.close()
        # sys.stdout.write(doc.toSource())
        # sys.stdout.write(doc.toSource())

# EOF

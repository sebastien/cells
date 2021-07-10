import sys
import json
from pathlib import Path
from . import Command
from ..parser import parse


# --
# The `Fmt` command is similar to the `Doc` command, but operates at a lower,
# simpler level where we format or export the core data structures. The `Doc`
# command will perform fancier transformations, such as indexing symbols
# and working with a set of documents to produce an output.
class Fmt(Command):

    NAME = "fmt"
    HELP = "Formats a cells document, or converts it to a different format"

    FORMATS = ["cd", "md", "json"]

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
        if not args.format in self.FORMATS:
            return self.err(f"'-t' option should be one of ${', '.join(self.FORMATS)}, got: {args.format}")
        if args.output == "-":
            out = sys.stdout
        else:
            out = open(args.output, "w")
        if args.format == "md":
            for chunk in doc.iterMarkdown():
                out.write(chunk)
        elif args.format == "json":
            json.dump(doc.toPrimitive(), out)
        else:
            for chunk in doc.iterSource():
                out.write(chunk)
        if out != sys.stdout:
            out.close()

# EOF

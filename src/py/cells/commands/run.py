from . import Command
from ..parser import parse
from ..kernel.python import PythonKernel
from ..kernel.markdown import MarkdownKernel
from ..kernel.meta import MetaKernel
from pathlib import Path
import sys


class Run(Command):

    NAME = "run"
    HELP = "Runs the document"

    def define(self, parser):
        super().define(parser)
        parser.add_argument("--session", help="Session identifier")
        parser.add_argument(
            "--with-source", help="Outputs source as well", action="store_true")
        parser.add_argument("files", metavar="FILE", type=str, nargs='+',
                            help='Input files to parse')

    def run(self, args):
        doc = parse(*(Path(_) for _ in args.files))
        # We create a type mapping and normalize the list of types
        types = {
            "python|py": PythonKernel(),
            "markdown|md": MarkdownKernel(),
        }
        normalized_types = {}
        def normalize_type(_): return normalized_types.get(_, _)
        for l in (_ for _ in (_.split("|") for _ in types) if _):
            for v in l[1:]:
                normalized_types[v] = l[0]

        kernel = MetaKernel(types)
        session = "a"
        for cell in doc.iterCells():
            cell.type = normalize_type(cell.type or "markdown")
            kernel.set(session, cell.ref, cell.inputs,
                       cell.source, cell.type or "markdown")
        # TODO: We should support other formats that JSON, such as HTML
        # or Markdown.
        for cell in doc.iterCells():
            value = kernel.get(session, cell.ref)
            if args.with_source:
                for line in cell.iterSource():
                    sys.stdout.write(line)
                sys.stdout.write(f"==\n")
            else:
                sys.stdout.write(f"== {cell.name}\n" if cell.name else "==\n")
            for line in json.dumps(value, indent=1).split("\n"):
                sys.stdout.write("\t")
                sys.stdout.write(line)
                sys.stdout.write("\n")

# EOF

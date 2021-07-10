import re
import sys
from subprocess import Popen
from pathlib import Path
from . import Command
from ..parser import parse
try:
    import texto
except ImportError:
    texto = None


def ensure_dir(path: Path) -> bool:
    if path and not path.exists():
        path.mkdir(parents=True)
    return path.is_dir()


def document(path: Path, format: str) -> str:
    """Returns a document in the given `format` representing the cells
    document at the given `path`."""
    doc = parse(path)
    md = "".join(_ for _ in doc.iterMarkdown())
    if format in ("md", "markdown"):
        return md
    elif format == "pdf":
        # TODO: We should detect if texto is available or not.
        # process = Popen(["pandoc", f"-t{format}"])
        pass
    else:
        # NOTE: Texto is not great ATM with markdown->markdown conversions,
        # but that's OK.
        return texto.render(texto.parse(md), format)


# --
# TODO: Should generate an index of cells (symbols) and an index of keywords,
# or maybe we generate this using a separate command.

# --
# TODO: At the very least, we should generate a catalogue of the notebooks
# as well as the sections. We could easily do that with a summarizer.

# --
# TODO: Doc should also generate an index of terms and symbols, as well as
# the graph of dependencies. By default, doc can be used like `fmt`, but if the
# output is a directory, will create one file per output, otherwise will put
# everything into one big file.
class Doc(Command):
    """Generates human-readable documentation files out of a set of input 
    documents."""

    NAME = "doc"
    HELP = "Generates documentation from a set of files"

    FORMATS = ["md", "json"] + (["html", "xml"] if texto else []) + ["pdf"]
    ALIASES = {"md": "markdown"}

    def define(self, parser):
        super().define(parser)
        parser.add_argument("-t", "--to", dest="format", action="store", default=self.FORMATS[0],
                            help=f"Output format: {', '.join(self.FORMATS)}")
        parser.add_argument("-o", "--output", dest="output", action="store", default="-",
                            help=f"Output file or directory")
        parser.add_argument("files", metavar="FILE", type=str, nargs='*',
                            help='Input files to format')

    def run(self, args):
        # We get the input files
        sources = []
        for path in (Path(_) for _ in args.files):
            if not path.exists():
                pass
            if path.is_file():
                sources.append(path)
        # We validate the arguments
        if not texto:
            return self.err(
                "'texto' package is missing, can't use the -t option: python -m pip install texto")
        if not args.format in self.FORMATS:
            return self.err(f"'-t' option should be one of ${', '.join(self.FORMATS)}, got: {args.format}")
        output_ext = f".{args.format}"
        output_path = Path(args.output)
        output_format = self.ALIASES.get(args.format, args.format)
        if not sources:
            pass
        elif len(sources) == 1:
            # Rule: if we have a single argument, then the output is file
            with open("/dev/stdout" if args.output == "-" else args.output, "wt") as f:
                f.write(document(sources[0], output_format))
        else:
            # Rule: if we have multiple arguments, then the output is a directory
            if not ensure_dir(output_path):
                return self.err(f"Output path should be a directory when multiple arguments are given, got: {output_path} for {args.files}")
            for path in sources:
                try:
                    doc = document(path, output_format)
                except Exception as e:
                    self.err(f"Could not process file '{path}': {e}")
                if doc:
                    target = output_path.joinpath(path).with_suffix(output_ext)
                    ensure_dir(target.parent)
                    with open(target, "wt") as f:
                        self.out(f"Creating {target} from {path}")
                        f.write(doc)
# EOF

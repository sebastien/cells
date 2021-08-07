import re
import sys
from typing import Iterable, Tuple
from subprocess import Popen
from pathlib import Path
from ..model import Cell
from ..kernel import loadKernels
from ..kernel.markdown import parseMarkdown, renderMarkdown
from ..parser import parse
from . import Command

try:
    import texto
except ImportError as e:
    raise ImportError(
        "Missing 'texto', run: python -m pip install --user texto-markup")

try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, get_lexer_for_filename, get_lexer_for_mimetype
    from pygments.formatters import HtmlFormatter
except ImportError as e:
    raise ImportError(
        "Missing 'pygments', run: python -m pip install --user Pygments")


HTML_PAGE_PRE = """\
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8"/>
    <title>${TITLE}</title>
    <link rel="stylesheet" href="stylesheet.css" />
    <meta name="viewport" content="width=device-width, initial-scale=1">
  </head>
  <body class="document">
"""

HTML_PAGE_POST = """\
    </body>
</html>
"""

# --
# # Documentation Command


def ensure_dir(path: Path) -> Path:
    """Ensures that the given path is a directory, creating it if necessary"""
    if path and not path.exists():
        path.mkdir(parents=True)
    assert path.is_dir()
    return path


def render(path: Path, format: str) -> Iterable[Tuple[Cell, str, str]]:
    if format == "html":
        yield from renderHTML(path)
    else:
        raise ValueError(f"Unsupported format: {format}")


def renderHTML(path: Path) -> Iterable[Tuple[Cell, str, str]]:
    """Returns a document in the given `format` representing the cells
    document at the given `path`."""
    doc = parse(path)
    for cell in doc.cells:
        cell_type = cell.type or "markdown"
        if cell_type == "markdown":
            # NOTE: Texto actually works better than mistune there, and also
            # provides more opportunities for extensions.
            # ~~
            # print(parseMarkdown(cell.source))
            # html = renderMarkdown(cell.source)
            html = texto.render(texto.parse(cell.source))
            yield (cell, cell_type, html)
        else:
            lexer = get_lexer_by_name(cell_type, stripall=True)
            formatter = HtmlFormatter(linenos=True, cssclass="source")
            html = highlight(cell.source, lexer, formatter)
            yield (cell, cell_type, html)


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
    """Generates renderer HTML files out of a set of input
    cell documents."""

    NAME = "doc"
    HELP = "Generates documentation from a set of files"

    FORMATS = ["html"]
    FORMAT_ALIAS = {}

    def define(self, parser):
        super().define(parser)
        parser.add_argument("-t", "--to", dest="format", action="store", default=self.FORMATS[0],
                            help=f"Output format: {', '.join(self.FORMATS)}")
        parser.add_argument("-o", "--output", dest="output", action="store", default="docs/cells",
                            help=f"Output director")
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
        if not args.format in self.FORMATS:
            return self.err(f"'-t' option should be one of {', '.join(self.FORMATS)}, got: {args.format}")
        output_ext = f".{args.format}"
        output_path = ensure_dir(Path(args.output))
        if not sources:
            # TODO: Should find the sources that have a cell comment and
            # integrate them.
            print("No sources")
        else:
            # Rule: if we have multiple arguments, then the output is a directory
            if not ensure_dir(output_path):
                return self.err(f"Output path should be a directory when multiple arguments are given, got: {output_path} for {args.files}")
            for path in sources:
                chunks = []
                try:
                    chunks = render(path, args.format)
                except Exception as e:
                    self.err(f"Could not process file '{path}': {e}")
                if chunks:
                    target = output_path.joinpath(path).with_suffix(output_ext)
                    ensure_dir(target.parent)
                    self.info(f"Writing: {target}")
                    with open(target, "wt") as f:
                        f.write(HTML_PAGE_PRE)
                        for cell, cell_type, html in chunks:
                            f.write(f'<section class="{cell_type}">')
                            f.write(html)
                            f.write(f'</section>')
                        f.write(HTML_PAGE_POST)


# EOF

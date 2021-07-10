import re
import sys
from pathlib import Path
from . import Command
from ..parser import parse
try:
    import texto
except ImportError:
    pass

HTML = """\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head><meta charset="utf8" /><style type="text/css">
{style}
</style></head>
<body>{body}</body>
</html>
"""

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Fraunces&Source+Code+Pro:ital,wght@0,300;0,400;0,500;0,600;0,700;0,900;1,300;1,400;1,500;1,600;1,700;1,900&display=swap');

:root {

    --color-text: #222936;
    --color-code-bg: #ececec;
    --color-code: #001843;

}


body {
	padding: 80px;
	color: #222222;
	font-family: 'Fraunces', serif;
	font-size: 16px;
	line-height: 22px;
}

p, h1, h2, h3, h4, h5, h6 {
	font-size: 16px;
	line-height: 22px;
}

pre {
    background-color: var(--color-code-bg);
    padding: 13px;
    padding-top: 6px;
    border-radius: 4px;
    overflow: auto;
}

code {
    color: var(--color-code);
}

code, pre {
	font-family: 'Source Code Pro', monospace;
    font-size: 13px;
	line-height: 11px;
}


pre {
}
"""


class Doc(Command):

    NAME = "doc"
    HELP = "Generates documentation from a set of files"

    FORMATS = ["html", "md"]
    EXT = [".py", ".js"]

    def define(self, parser):
        super().define(parser)
        parser.add_argument("-t", "--to", dest="format", action="store", default="html",
                            help=f"Output format: {', '.join(self.FORMATS)}")
        parser.add_argument("-o", "--output", dest="output", action="store",
                            help=f"Output directory")
        parser.add_argument("files", metavar="FILE", type=str, nargs='*',
                            help='Input files to format')

    def run(self, args):
        # Step 1: We get the files
        sources = []
        for path in (Path(_) for _ in args.files):
            if not path.exists():
                pass
            if path.is_file():
                sources.append(path)
        ext = f".{args.format}"
        out = sys.stdout if args.output in (None, "-") else None
        # TODO: Invalidated
        # Step 2: Ensuring that output exists
        # output = Path(args.output) if args.output else None
        # if output and not output.exists():
        #     output.mkdir(parents=True)
        # Step 3: Generating the files
        for path in sources:
            doc = parse(path)
            md = "".join(_ for _ in doc.iterMarkdown())
            res = texto.render(texto.parse(md), args.format)
            out.write(res)
            # out.write(HTML.format(body=res, style=CSS))
            # with open(target := output.joinpath(path).with_suffix(ext), "wt") as f:
            #     self.out(f"Creating {target}")
            #     f.write(HTML.format(body=res, style=CSS))
# EOF

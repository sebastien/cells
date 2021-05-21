import sys
import re
import json
import argparse
from typing import Iterable
from pathlib import Path
from .parser import Parser, parse
from .kernel.meta import MetaKernel
from .kernel.python import PythonKernel
from .kernel.markdown import MarkdownKernel


class Command:

    NAME = ""
    HELP = ""

    def define(self, parser):
        pass

    def run(self, args):
        print(args)

    def __call__(self, args=sys.argv[1:] if len(sys.argv) > 1 else []):
        parser = argparse.ArgumentParser(prog=self.NAME, help=self.HELP)
        self.define(parser)
        options, args = parser.parse_known_args(args)
        return self.run(options)


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


def extractLines(lines: Iterable[str], lang, prefix=re.compile(r"^#( (?P<rest>.*)|\s*)$")):
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

    def define(self, parser):
        super().define(parser)
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
        for chunk in doc.iterMarkdown():
            sys.stdout.write(chunk)
        # sys.stdout.write(doc.toSource())
        # sys.stdout.write(doc.toSource())


def command(args):
    # FROM: https://stackoverflow.com/questions/10448200/how-to-parse-multiple-nested-sub-commands-using-python-argparse
    parser = argparse.ArgumentParser(prog="cells")
    subparsers = parser.add_subparsers(
        help="Available subcommands", dest='subcommand')
    # We register the subcommands
    cmds = dict((_.NAME, _()) for _ in [Run, FMT])
    for _ in cmds.values():
        _.define(subparsers.add_parser(_.NAME, help=_.HELP))
    parsed = None
    rest = args
    while rest:
        p, rest = parser.parse_known_args(rest)
        if p.subcommand:
            parsed = p
        if not p.subcommand:
            break
    # We could not parse everything
    if rest:
        raise ValueError("Cannot parse the command", parsed, rest)
    elif parsed and parsed.subcommand:
        cmds[parsed.subcommand].run(parsed)


def run(args=sys.argv[1:]):
    return command(args)

    # EOF

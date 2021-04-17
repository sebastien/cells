import sys
import argparse
import json
from pathlib import Path
from cells.parser import parse


class Command:

    NAME = None
    HELP = None

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
        parser.add_argument("files", metavar="FILE", type=str, nargs='+',
                            help='Input files to parse')


class FMT(Command):

    NAME = "fmt"
    HELP = "Formats the document"

    def define(self, parser):
        super().define(parser)
        parser.add_argument("files", metavar="FILE", type=str, nargs='?',
                            help='Input files to parse')


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

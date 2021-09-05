import sys
import argparse
from .commands.fmt import Fmt
from .commands.run import Run
from .commands.doc import Doc
from .commands._import import Import

COMMANDS = [Run, Fmt, Doc, Import]


def run(args: list[str] = sys.argv[1:]):
    """Runs the given command, as passed from the command line"""
    # FROM: https://stackoverflow.com/questions/10448200/how-to-parse-multiple-nested-sub-commands-using-python-argparse
    if not args:
        args = ["--help"]
    parser = argparse.ArgumentParser(prog="cells")
    subparsers = parser.add_subparsers(
        help="Available subcommands", dest='subcommand')
    # We register the subcommands
    cmds = dict((_.NAME, _()) for _ in COMMANDS)
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


if __name__ == "__main__":
    run()
# EOF

# EOF

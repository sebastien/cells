import sys
import argparse
import json
from cells.parser import Parser


def run(args=sys.argv[1:]):
    # We create the parse and register the options
    parser = argparse.ArgumentParser(prog="cells")
    parser.add_argument("inputs", metavar="FILE", type=str, nargs='+',
                        help='Input files to parse')
    args = parser.parse_args(args)
    cells_parser = Parser()
    for path in args.inputs:
        cells_parser.start()
        with open(path) as f:
            for line in f.readlines():
                cells_parser.feed(line)
        doc = cells_parser.end()
        json.dump(doc.toPrimitive(), sys.stdout)

# EOF

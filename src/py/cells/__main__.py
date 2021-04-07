from .parser import *
import sys

parser = Parser()
with open(sys.argv[1]) as f:
    for line in f.readlines():
        print(parser.parseLine(line))

# EOF

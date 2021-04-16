from .parser import *
from .model import Cell
import sys

parser = Parser()
parser.start()
with open(sys.argv[1]) as f:
    for line in f.readlines():
        parser.feed(line)

print(parser.end().toPrimitive())
# EOF

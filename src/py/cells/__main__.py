from .parser import *
from .model import Cell
from .dag import DAG
import sys

parser = Parser()
parser.start()
with open(sys.argv[1]) as f:
    for line in f.readlines():
        parser.feed(line)

# print(parser.document.toPrimitive())
dag = DAG[Cell]()

for cell in parser.document.cells:
    dag.setNode(cell.ref, cell.id)
    dag.addInputs(cell.ref, cell.inputs)

print(dag.toPrimitive())
for cell, rank in dag.ranks().items():
    print(f"{cell}: {rank}")

print(dag.successors())

# EOF

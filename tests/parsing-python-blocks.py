from cells.parsing.python import Python
from cells.parsing import Symbol

# -- ASSIGNMENTS
for i in range(2):
    path = __file__.replace(".py", f"+D{i+1:02d}.py")
    print(f" -- TEST: {path}")
    with open(path) as f:
        for cell in Python.Cells(f.read()):
            print(cell.asDict())
# EOF

from cells.parsing.python import Python
from cells.kernel.python import PythonKernel
from cells.parsing import Symbol

SOURCE = """\
a = 10_00
b='Hello, World!'
def f(c):
    print(a,b,c)
"""
slots = []
kernel = PythonKernel()
session = "S001"
for sym in Python.Symbols(SOURCE):
    s, e = sym.range
    text = SOURCE[s:e]
    print("SETTING SLOT", sym.name, sym.inputs, "FROM", sym)
    kernel.set(session, sym.name, sym.inputs, text, "python")
    slots.append((session, sym.name))

for s, n in slots:
    kernel = PythonKernel()
    print(s, n, kernel.evalSlot(s, n))

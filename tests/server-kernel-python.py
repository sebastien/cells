from cells.parsing.python import Python
from cells.kernel.python import PythonKernel
from cells.parsing import Symbol

# --
# Ensures that the evaluation of slots works


SOURCE = """\
a = 10_00

b='Hello, World!'

"Anonymous slot"

def f(c):
    return (a,b,c)
"""
slots = []
kernel = PythonKernel()
session = "S001"
for sym in Python.Symbols(SOURCE):
    s, e = sym.range
    text = SOURCE[s:e]
    kernel.set(session, sym.name, sym.inputs, text, "python")
    slots.append((session, sym.name))


SLOTS = {
    "a": lambda _: _ == 1000,
    "b": lambda _: _ == "Hello, World!",
    "f": lambda _: _('c') == (1000, 'Hello, World', 'c'),
}
for s, name in slots:
    value = kernel.evalSlot(s, name)
    print(f"-- TEST: Slot {name}")
    print(f"   value: {value}")
    assert name in SLOTS, f"Unexpected slot name: {name}"
    print(f"   predicate: {SLOTS[name]}")
    assert SLOTS[name](value)
    print(f".. OK: {value}")
 # EOF

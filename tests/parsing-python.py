from cells.parsing.python import Python
import harness
from tree_sitter import Node
from pprint import pprint
import re

EXAMPLES = """
# -- ASSIGNMENTS
# symbols: value
value = [1, 2, 3, 4]

# -- NESTED_ASSIGNMENT
# symbols: value, f, f.value
value = [1, 2, 3, 4]
def f():
    value = [1, 2, 3, 4]

# -- FUNCTION_DEFINITION
# symbols: f
def f(a, b, c, d):
    pass

# -- REFERENCES
# This is one anonymous scope:
# inputs: a, b
a + b


# -- XXX
# This is one named scope, f:
# symbols: f
# inputs: a, b, arg1
def f():
    a + b + arg1


# -- XXX
# This is one named scope, g:
# symbols: g
# inputs: f,a,b,do_something_there,one,two
def g(arg0, arg1, arg=2 + a + b):
    f(a + b)
    if True:
        do_something_there(one, two)


# -- CLASS
# symbols: A, A.static, A.method
class A:
    STATIC = 1

    def method(self, a, b, c):
        # Self reference
        return A.STATIC

"""


print(f"INFO Examples: {', '.join(_ for _ in EXAMPLES)}")

# SEE: https://tree-sitter.github.io/tree-sitter/using-parsers#query-syntax
examples = harness.parseExamples(EXAMPLES)
print(examples)
for k, example in examples.items():
    print(f"STA Example {k}")
    for line in example.code.split("\n"):
        if line.strip():
            print("---", line.rstrip("\n"))
    # print("OUT:sexp=", parser.sexp(example))
    # DataflowProcessor(parser)(example)
    print("OUT symbols=", Python.Symbols(example.code))
    print(f"END {k}\n")

# EOF

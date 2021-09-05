from cells.parsing.python import Python
from tree_sitter import Node
from pprint import pprint
import re

# -- ASSIGNMENTS
with open(__file__.replace(".py", "-examples.py")) as f:
    RE_SEP = re.compile(r"# -- ([A-Z_]+)\n")
    text = f.read()
    examples = {}
    current = []
    offset = 0
    for match in RE_SEP.finditer(text):
        current.append(text[offset:match.start()])
        offset = match.end()
        examples[match.group(1)] = current = []
    current.append(text[offset:])
    EXAMPLES = dict((k, ''.join(v)) for k, v in examples.items())


print(f"INFO Examples: {', '.join(_ for _ in EXAMPLES)}")

# SEE: https://tree-sitter.github.io/tree-sitter/using-parsers#query-syntax
example = EXAMPLES["REFERENCES"]
# print(parser.sexp(example))
# DataflowProcessor(parser)(example)
Python.Symbols(example)

# EOF

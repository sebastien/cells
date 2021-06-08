from cells.parser import Parser
from cells.diff import equals

parser = Parser()


def expects(expr, expected):
    value = parser.parseDefinition(expr).value
    assert equals(value, expected), f"Expected {expected}, got: {value}"


# Names
expects("doc", {"name": "doc"})
# Names: quoted
expects('"doc.md"', {"name": "doc.md"})
# Types: anonymous
expects(":python", {"type": "python"})
# Types: qualified
expects("a:python", {"name": "a", "type": "python"})
# Inputs: single
expects("a < b", {"name": "a", "inputs": ["b"]})
# Inputs: single quoted
expects('a < "b"', {"name": "a", "inputs": ["b"]})
# Inputs: multiple
expects("a < b c", {"name": "a", "inputs": ["b", "c"]})
# Modifiers: single
expects("a [hide]", {"name": "a", "modifiers": ["hide"]})

#     {"name":"result","type":"shell"}
# # Inputs
# a < b
#     {"name":"a","inputs":["a"]}
# # Inputs: multiple
# a < b c
#     {"name":"a","inputs":["a", "b"]}
# # Inputs: quoted
# a < "b" "c"
#     {"name":"a","inputs":["a", "b"]}
# # Modifiers
# a [indented]
# """.split("\n") if _.strip()]
#
# section = "General"
# cases = []
# for line in CASES:
#     if line.startswith("#"):
#     if line.startswith("    "):

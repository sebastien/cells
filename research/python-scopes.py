# --
# # Python dynamic scopes
#
# Cells Python's kernel needs to know which values are accessed from
# a cell's code, and which values are defined by the cell.
#
# To explore that, we start with overriding a dict object.

from typing import Any


class DynamicScope(dict):

    def __init__(self):
        super().__init__()
        self.accessed = []
        self.defined = []
        self.values = {}

    def __getitem__(self, k: str) -> Any:
        self.accessed.append(k)
        return self.values.get(k)

    def __setitem__(self, k: str, v) -> Any:
        self.defined.append(k)
        self.values[k] = v

# --
# And now we can try to run code and see if the symbols are defined
# as we expected.


scope = DynamicScope()
assert eval("(a,b,c)", scope) == (None, None, None)
assert scope.accessed == ["a", "b", "c"]

# --
# We can also validate the definition of elements in the scope
exec("a = 1;b = 2;c=4", scope)
assert scope.defined == ["a", "b", "c"], scope.defined
assert scope.accessed == ["a", "b", "c"]

# --
# Another option is to retry as many times as we need and define
# the symbols as required. That's certainly not the best approach,
# as it will re-excute the code many times.
resolved = False
scope = {}
while not resolved:
    try:
        eval("a + b", scope, scope)
        resolved = True
    except NameError as e:
        sym = e.args[0].split("'")[1]
        scope[sym] = 1
# EOF

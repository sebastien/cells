from cells.kernel.parsing import PythonParser, Processor, Scope, Symbol
from tree_sitter import Node
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
parser = PythonParser

# SEE: https://tree-sitter.github.io/tree-sitter/using-parsers#query-syntax

ASSIGNMENT_QUERY = "(assignment left: (identifier) @name)"

assert parser.query(ASSIGNMENT_QUERY, EXAMPLES["ASSIGNMENTS"]) == {
    "name": "value"}


class DataflowProcessor(Processor):

    def init(self):
        self.root = Scope()
        self.scope = self.root
        self.mode = None
        self.defs = set()
        self.refs = set()
        self.symbols: dict[str, Symbol] = {}

    def on_end(self):

        defs = set()
        refs = set()

        def define(scope: Scope):
            for slot, mode in scope.slots.items():
                if mode == "def":
                    defs.add(slot)

        def walk(scope: Scope):
            for slot, mode in scope.slots.items():
                if mode == "ref" and not scope.defines(slot):
                    refs.add(slot)

        define(self.root)
        [define(_) for _ in self.root.children]

        self.root.walk(walk)
        print(self.root.asDict())
        print("Defs", defs)
        print("Refs", refs)

    def on_expression_statement(self, node: Node, value: str, depth: int, breadth: int):
        mode = self.mode
        self.mode = "ref"

        def on_exit(_):
            self.mode = mode
        return on_exit

    def on_binary_operator(self, node: Node, value: str, depth: int, breadth: int):
        mode = self.mode
        self.mode = "ref"

        def on_exit(_):
            self.mode = mode
        return on_exit

    def on_function_definition(self, node: Node, value: str, depth: int, breadth: int):
        self.scope = self.scope.derive()
        self.mode = "def"

        def on_exit(_, self=self):
            self.scope = self.scope.parent
        return on_exit

    def on_identifier(self, node: Node, value: str, depth: int, breadth: int):
        if value not in self.scope.slots:
            self.scope.slots[value] = self.mode
            if self.mode == "def":
                self.defs.add(value)
                if value in self.refs:
                    self.refs.remove(value)
            elif self.mode == "ref" and not self.scope.defines(value):
                self.refs.add(value)

    def on_node(self, node: str, value: str, depth: int, breadth: int):
        pass


print(parser.sexp(EXAMPLES["REFERENCES"]))
DataflowProcessor(parser)(EXAMPLES["REFERENCES"])

# EOF

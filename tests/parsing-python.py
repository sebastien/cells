from cells.kernel.parsing import PythonParser, Processor, Scope, Symbol, extract
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
parser = PythonParser

# SEE: https://tree-sitter.github.io/tree-sitter/using-parsers#query-syntax

ASSIGNMENT_QUERY = "(assignment left: (identifier) @name)"

assert parser.query(ASSIGNMENT_QUERY, EXAMPLES["ASSIGNMENTS"]) == {
    "name": "value"}


class DataflowProcessor(Processor):

    def init(self):
        self.root = Scope(type="module")
        self.scope = self.root
        self.mode = None
        self.defs = set()
        self.refs = set()
        self.symbols: dict[str, Symbol] = {}

    def on_end(self):

        symbols = {}

        def walk(scope: Scope, depth: int):
            if depth == 1 or scope.qualname:
                name = scope.qualname or f"#{len(symbols)}"
                symbols[name] = Symbol(name=name, scope=scope)
            #    defs.add(scope.qualname)
            # for ref, _ in scope.refs.items():
            #    if not scope.isDefined(ref):
            #        refs.add(ref)

        self.root.walk(walk)
        pprint(self.root.asDict())
        print(symbols)

    # --
    # ### Definitions

    def on_function_definition(self, node: Node, value: str, depth: int, breadth: int):
        return self.on_definition(node, value, depth, breadth, "function")

    def on_class_definition(self, node: Node, value: str, depth: int, breadth: int):
        return self.on_definition(node, value, depth, breadth, "class")

    def on_assignment(self, node: Node, value: str, depth: int, breadth: int):
        # TODO: We're not handling the asssignment properly, ie.
        # class A:
        #   STATIC = 1
        #   SOMEVAR[1] = 10
        #   A,B = (10, 20)
        pass

    def on_definition(self, node: Node, value: str, depth: int, breadth: int, type: str = "block"):
        name_node = node.child_by_field_name("name")
        name = extract(name_node, self.code) if name_node else None
        self.scope = self.scope.derive(
            type=type, range=(node.start_byte, node.end_byte), name=name)
        self.mode = "def"

        def on_exit(_, self=self):
            self.scope = self.scope.parent
        return on_exit

    # --
    # ### References
    def on_identifier(self, node: Node, value: str, depth: int, breadth: int):
        if value not in self.scope.slots:
            if self.mode == "ref":
                self.scope.refs[value] = self.mode
            else:
                self.scope.slots[value] = self.mode

    def on_return_statement(self, node: Node, value: str, depth: int, breadth: int):
        return self.on_statement(node, value, depth, breadth)

    def on_expression_statement(self, node: Node, value: str, depth: int, breadth: int):
        if self.scope.type != "module":
            return self.on_statement(node, value, depth, breadth)
        else:
            self.scope = self.scope.derive(
                type="expression", range=(node.start_byte, node.end_byte))
            self.mode = "def"
            self.on_statement(node, value, depth, breadth)

            def on_exit(_, self=self):
                self.scope = self.scope.parent
            return on_exit

    def on_statement(self, node: Node, value: str, depth: int, breadth: int):
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

    def on_node(self, node: str, value: str, depth: int, breadth: int):
        pass


example = EXAMPLES["REFERENCES"]
print(parser.sexp(example))
DataflowProcessor(parser)(example)

# EOF

from cells.kernel.parsing import PythonParser
from tree_sitter import Tree, Node
from typing import Optional


def parse(text: str):
    return PythonParser(text).root_node


def sexp(text: str):
    return PythonParser(text).root_node.sexp()


def extract(node: Node, text: str) -> str:
    return text[node.start_byte:node.end_byte]


def query(query: str, code: str) -> dict[str, str]:
    return dict((k, extract(v, code)) for v, k in PythonParser.query(
        query).captures(parse(code)))


def node_key(node: Node) -> str:
    return f"{node.type}:{node.start_byte}:{node.end_byte}"


class Processor:

    ALIASES = {
        "+": "plus",
        "-": "minus",
        "*": "times",
        "/": "slash",
        "**": "timetime",
        "^": "chevron",
    }

    def __init__(self, code: Optional[str] = None):
        self.init()
        if code:
            self.__call__(code)

    def init(self):
        pass

    def on_node(self, node: str, value: str, depth: int, breadth: int):
        print(f"node:{node} {depth}+{breadth}: {value}")

    def on_end(self):
        pass

    def __call__(self, code: str):
        tree = parse(code)
        cursor = tree.walk()
        depth = 0
        breadth = 0
        visited = set()
        on_exit = {}
        while True:
            node = cursor.node
            key = node_key(node)
            method_name = f"on_{node.type}"
            processor = getattr(self, method_name) if hasattr(
                self, method_name) else self.on_node
            exit_functor = processor(
                node.type, extract(node, code), depth, breadth)
            # We use functors as exit functions
            if exit_functor:
                print("WILL EXIT ON", key)
                if node.child_count > 0:
                    on_exit[key] = exit_functor
                else:
                    exit_functor(node)
            visited.add(node_key(node))
            if cursor.goto_first_child():
                breadth = 0
                depth += 1
            elif cursor.goto_next_sibling():
                breadth += 1
            else:
                # When we go up, we need to be careful.
                previous_key = node_key(cursor.node)
                while depth > 0:
                    print("*** EXITING", previous_key)
                    previous_node = cursor.node
                    breadth = 0
                    cursor.goto_parent()
                    current_key = node_key(cursor.node)
                    if current_key == previous_key:
                        break
                    else:
                        if previous_key in on_exit:
                            on_exit[previous_key](previous_node.type)
                        previous_key = current_key
                    depth -= 1
                    # We skip the visited nodes
                    while node_key(cursor.node) in visited:
                        if cursor.goto_next_sibling():
                            breadth += 1
                        else:
                            break
                    if node_key(cursor.node) not in visited:
                        break
                if node_key(cursor.node) in visited:
                    self.on_end()
                    break


ASSIGNMENT = """
value = [1,2,3,4]
"""

# SEE: https://tree-sitter.github.io/tree-sitter/using-parsers#query-syntax

ASSIGNMENT_QUERY = """
(assignment left: (identifier) @name)
"""


assert query(ASSIGNMENT_QUERY, ASSIGNMENT) == {"name": "value"}

NESTED_ASSIGNMENT = """
def f():
    value = [1,2,3,4]
"""

# print(sexp(NESTED_ASSIGNMENT))
# print(query(ASSIGNMENT_QUERY, NESTED_ASSIGNMENT))

FUNCTION_DEFINITION = """
def f(a,b,c,d):
    pass
"""

REFERENCES = """
a + b

def f():
    a + b + arg1

def g(arg0,arg1,arg=2+a+b):
    f(a + b)
    if True:
        do_something_there(one, two)

"""


class Scope:
    def __init__(self, parent=None):
        self.slots = {}
        self.children = []
        self.parent = parent
        if parent:
            parent.children.append(self)

    def defines(self, name: str) -> bool:
        return self.slots.get(name) == "def" or self.parent and self.parent.defines(name)

    def derive(self):
        return Scope(self)

    def walk(self, functor):
        functor(self)
        for _ in self.children:
            _.walk(functor)

    def asDict(self):
        return dict(
            slots=self.slots,
            children=[_.asDict() for _ in self.children]
        )


class DataflowProcessor(Processor):

    def init(self):
        self.root = Scope()
        self.scope = self.root
        self.mode = None
        self.defs = set()
        self.refs = set()

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

    def on_expression_statement(self, node: str, value: str, depth: int, breadth: int):
        mode = self.mode
        self.mode = "ref"

        def on_exit(_):
            self.mode = mode
        return on_exit

    def on_binary_operator(self, node: str, value: str, depth: int, breadth: int):
        mode = self.mode
        self.mode = "ref"

        def on_exit(_):
            self.mode = mode
        return on_exit

    def on_function_definition(self, node: str, value: str, depth: int, breadth: int):
        self.scope = self.scope.derive()
        self.mode = "def"
        print("ENTER FUNCTION")

        def on_exit(_, self=self):
            self.scope = self.scope.parent
            print("EXIT FUNCTION")
        return on_exit

    def on_identifier(self, node: str, value: str, depth: int, breadth: int):
        if value not in self.scope.slots:
            self.scope.slots[value] = self.mode
            if self.mode == "def":
                print("DEF", value)
                self.defs.add(value)
                if value in self.refs:
                    self.refs.remove(value)
            elif self.mode == "ref" and not self.scope.defines(value):
                print("REF", value)
                self.refs.add(value)

    def on_node(self, node: str, value: str, depth: int, breadth: int):
        pass


print(sexp(REFERENCES))
DataflowProcessor(REFERENCES)

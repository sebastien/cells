from . import TSParser, TSProcessor, Scope, Symbol
from tree_sitter import Node


class TSPythonProcessor(TSProcessor):

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
                if scope.qualname or scope.children:
                    name = scope.qualname or f"_S{len(symbols)}"
                    symbols[name] = Symbol(name=name, scope=scope)

        self.root.walk(walk)
        return [_ for _ in symbols.values()]

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
        name_node = node.child_by_field_name("left")
        name = self.extract(name_node) if name_node else None
        self.scope = self.scope.derive(
            type=type, range=(node.start_byte, node.end_byte), name=name)

        def on_exit(_, self=self):
            self.scope = self.scope.parent
        return on_exit

    def on_definition(self, node: Node, value: str, depth: int, breadth: int, type: str = "block"):
        name_node = node.child_by_field_name("name")
        name = self.extract(name_node) if name_node else None
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

    # NOTE: Assignments are contained in expressions, so maybe not ideal
    # def on_expression_statement(self, node: Node, value: str, depth: int, breadth: int):
    #     print("ON:EXPR", node.sexp())
    #     if self.scope.type != "module":
    #         return self.on_statement(node, value, depth, breadth)
    #     else:
    #         self.scope = self.scope.derive(
    #             type="expression", range=(node.start_byte, node.end_byte))
    #         self.mode = "def"
    #         self.on_statement(node, value, depth, breadth)

    #         def on_exit(_, self=self):
    #             self.scope = self.scope.parent
    #         return on_exit

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


class Python:

    PROCESSOR = TSPythonProcessor(TSParser("python"))

    @classmethod
    def Symbols(cls, code: str) -> list[Symbol]:
        """Returns the list of symbols defined in the given code"""
        return cls.PROCESSOR(code)

# EOF

from . import TSParser, TSProcessor, Scope, Symbol
from tree_sitter import Node
from ..model import Cell


class TSPythonProcessor(TSProcessor):
    def init(self):
        self.root: Scope = Scope(type="module")
        self.scope = self.root
        self.mode = None
        self.defs = set()
        self.refs = set()
        self.symbols: dict[str, Symbol] = {}

    def on_start(self):
        super().on_start()
        self.symbols = {}

    def on_end(self) -> list[Symbol]:
        symbols = {}

        def walk(scope: Scope, depth: int):
            # Level 1 scopes may not have qualname
            if (depth == 1 or scope.qualname) and (scope.qualname or scope.children):
                # So we make suer there is a qualname
                name = scope.qualname or f"_S{len(symbols)}"
                # And we register the symbol definition
                # TODO: We should also output the dependencies as part of the symbol
                symbols[name] = Symbol(name=name, scope=scope)

        self.walkScope(self.root, walk)
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
            type=type, range=(node.start_byte, node.end_byte), name=name
        )

        def on_exit(_, self=self):
            self.scope = self.scope.parent

        return on_exit

    def on_definition(
        self, node: Node, value: str, depth: int, breadth: int, type: str = "block"
    ):
        name_node = node.child_by_field_name("name")
        name = self.extract(name_node) if name_node else None
        self.scope = self.scope.derive(
            type=type, range=(node.start_byte, node.end_byte), name=name
        )
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

    @classmethod
    def Cells(cls, code: str) -> list[Cell]:
        """Returns the list of cells identified as paret of the given code."""
        symbols: list[tuple[Symbol, int, int]] = []
        for symbol in cls.Symbols(code):
            s, e = symbol.range
            # We need to preserve the indentation
            while code[s - 1] in " \t" and s > 0:
                s -= 1
            if symbols and (last := symbols[-1]) and last[2] > s:
                symbols[-1] = (last[0], last[1], s - 1)
            symbols.append((symbol, s, e))
        res = []
        for symbol, start, end in symbols:
            # TODO: We should capture the overall indentation of the block
            res.append(
                Cell(
                    name=symbol.name,
                    type="python",
                    inputs=[_ for _ in symbol.inputs],
                    content=(code, start, end),
                )
            )
        return res


# EOF

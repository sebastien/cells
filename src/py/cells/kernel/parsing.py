from tree_sitter import Language, Node, Tree, Parser as TSParser
from typing import Optional, Callable, Any
from pathlib import Path

# --
# # Kernel Language Parsing
#
# This module uses Tree Sitter to take source code an identify the following:
#
# - The list of declarations (symbols) defined in the source code.
# - The dependencies of each declaration, ie. which symbols it uses.


# --
# Tree-Sitter needs to build binaries first, which is
# what we are doing here.

# NOTE: This only works when building from source
BASE_PATH = Path(__file__).parent.parent.parent.parent.parent
DEPS_PATH = BASE_PATH.joinpath("deps")
BUILD_PATH = BASE_PATH.joinpath("build")
LIBRARY_PATH = BUILD_PATH.joinpath("cells-treesitter.so")
LANGUAGES = ["python", "javascript", "go"]
Language.build_library(
    str(LIBRARY_PATH),
    [f"{DEPS_PATH}/tree-sitter-{_}" for _ in LANGUAGES]
)


def extract(node: Node, text: str) -> str:
    return text[node.start_byte:node.end_byte]


# --
# ## Language Parser

class Parser:
    def __init__(self, lang: str):
        self.lang = lang
        self.parser = TSParser()
        self.tsLang = Language(LIBRARY_PATH, lang)
        self.parser.set_language(self.tsLang)

    def parse(self, code: str) -> Node:
        return self(code).root_node

    def sexp(self, code: str) -> str:
        return self.parse(code).sexp()

    def query(self, query: str, code: str) -> dict[str, str]:
        return dict((k, extract(v, code)) for v, k in self.tsLang.query(
            query).captures(self.parse(code)))

    def __call__(self, value: str) -> Tree:
        return self.parser.parse(bytes(value, "utf8"))

# --
# ## Tree Processor


def node_key(node: Node) -> str:
    """Returns a unique identifier for a given node. Unicity is within
    a tree."""
    return f"{node.type}:{node.start_byte}:{node.end_byte}"


class Processor:
    """Base class to write TreeSitter processors."""

    ALIASES = {
        "+": "plus",
        "-": "minus",
        "*": "times",
        "/": "slash",
        "**": "timetime",
        "^": "chevron",
    }

    def __init__(self, parser: Parser):
        self.parser = parser
        self.init()

    def init(self):
        pass

    def on_node(self, node: Node, value: str, depth: int, breadth: int):
        print(f"node:{node.type} {depth}+{breadth}: {value}")

    def on_end(self):
        pass

    def __call__(self, code: str):
        tree = self.parser.parser.parse(bytes(code, "utf8"))
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
                node, extract(node, code), depth, breadth)
            # We use functors as exit functions
            if exit_functor:
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


class Symbol:
    def __init__(self, name: str, parent: Optional[str] = None):
        self.name = name
        self.parent = parent
        self.inputs: list[str] = []
        self.startOffset: int = 0
        self.endOffset: int = 0


class Scope:
    def __init__(self, parent: Optional['Scope'] = None):
        self.slots: dict[str, str] = {}
        self.children: list[Scope] = []
        self.parent: Optional[Scope] = parent
        if parent:
            parent.children.append(self)

    def defines(self, name: str) -> bool:
        return self.slots.get(name) == "def" or bool(self.parent and self.parent.defines(name))

    def derive(self) -> 'Scope':
        return Scope(self)

    def walk(self, functor: Callable[[Node], None]):
        functor(self)
        for _ in self.children:
            _.walk(functor)

    def asDict(self) -> dict[str, Any]:
        return dict(
            slots=self.slots,
            children=[_.asDict() for _ in self.children]
        )


# --
# ## Global Parsers

PythonParser = Parser("python")
JavascriptParser = Parser("javascript")
GoParser = Parser("go")

# EOF

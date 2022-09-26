from tree_sitter import Language, Parser

# --
# Ensures that tree-sitter is working properly and that the grammars
# are also working properly.

# FROM: https://github.com/tree-sitter/py-tree-sitter

DEPS = ".deps/src/"
BUILD = "build"
Language.build_library(
    # Store the library in the `build` directory
    f"BUILD/treesitter.so",
    # Include one or more languages
    [
        f"{DEPS}/tree-sitter-go",
        f"{DEPS}/tree-sitter-javascript",
        f"{DEPS}/tree-sitter-python",
    ],
)
GO_LANGUAGE = Language("build/treesitter.so", "go")
JS_LANGUAGE = Language("build/treesitter.so", "javascript")
PY_LANGUAGE = Language("build/treesitter.so", "python")

parser = Parser()
parser.set_language(PY_LANGUAGE)
tree = parser.parse(
    bytes(
        """
def foo():
    if bar:
        baz()
""",
        "utf8",
    )
)

print(tree)

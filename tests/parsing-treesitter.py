from tree_sitter import Language, Parser

# --
# Ensures that tree-sitter is working properly and that the grammars
# are also working properly.

# FROM: https://github.com/tree-sitter/py-tree-sitter

Language.build_library(
    # Store the library in the `build` directory
    'build/treesitter.so',

    # Include one or more languages
    [
        'deps/tree-sitter-go',
        'deps/tree-sitter-javascript',
        'deps/tree-sitter-python'
    ]
)
GO_LANGUAGE = Language('build/treesitter.so', 'go')
JS_LANGUAGE = Language('build/treesitter.so', 'javascript')
PY_LANGUAGE = Language('build/treesitter.so', 'python')

parser = Parser()
parser.set_language(PY_LANGUAGE)
tree = parser.parse(bytes("""
def foo():
    if bar:
        baz()
""", "utf8"))

print(tree)

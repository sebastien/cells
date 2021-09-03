from tree_sitter import Language, Tree, Parser as TSParser
from pathlib import Path

# --
# We're using Tree-Sitter as it has won the crown of parser king, being shipped
# in many editors now. Tree-Sitter needs to build binaries first, which is
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


class Parser:
    def __init__(self, lang: str):
        self.lang = lang
        self.parser = TSParser()
        self.tsLang = Language(LIBRARY_PATH, lang)
        self.parser.set_language(self.tsLang)

    def query(self, value: str):
        return self.tsLang.query(value)

    def __call__(self, value: str) -> Tree:
        return self.parser.parse(bytes(value, "utf8"))


PythonParser = Parser("python")
JavascriptParser = Parser("javascript")
GoParser = Parser("go")

# EOF

from ..model import Document, Cell
import sys
import json
from pathlib import Path
from . import Command
from ..parsing.python import Python
from .fmt import Fmt


# --
# The `Import` command will import an existing source code into a cells
# documnet.
class Import(Fmt):

    NAME = "import"
    HELP = "Import an existing source code, generating a cells document"

    LANG = ["py", "js", "jsx"]

    def parse(self, inputs: list[Path]) -> Document:
        doc = Document()
        for path in inputs:
            text = path.read_text()
            offset = 0
            for symbol in Python.Symbols(text):
                inbetween = text[offset:symbol.range[0]].strip()
                if inbetween:
                    doc.add(Cell(type="python", content=inbetween))
                content = text[symbol.range[0]:symbol.range[1]]
                cell = Cell(name=symbol.name, type="python", inputs=[
                            _ for _ in symbol.inputs], content=content)
                offset = symbol.range[1]
                doc.add(cell)
        doc.prepare()
        return doc

# EOF

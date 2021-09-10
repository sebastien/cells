from retro import Request, Response, Component, on, run
from retro.contrib.api import acors
from ..parsing.python import Python
from ..parsing import Symbol
from ..model import Document, Cell
import json


def aon(**kwargs):
    """Like @on, but with async CORS support."""
    kwargs.setdefault("OPTIONS", next((_ for _ in kwargs.values()), None))
    return lambda _, kwargs=kwargs: (on(**kwargs)(acors()(_)))


cell = Cell()


class KernelAPI(Component):

    @aon(POST="eval/python")
    async def runPython(self, request: Request) -> Response:
        data = await request.data()
        if not data:
            return request.returns(True)
        else:
            source = json.loads(str(data, "utf8"))
            print("PYTHON", source)
            return request.returns(True)


class ParseAPI(Component):

    @aon(POST="parse/python")
    async def parsePython(self, request: Request) -> Response:
        data = await request.data()
        if not data:
            return request.returns(True)
        else:
            source = json.loads(str(data, "utf8"))
            symbols = Python.Symbols(source)
            return request.returns(symbols)


class EditorAPI(Component):

    @aon(POST="doc")
    async def createDocument(self, request: Request) -> Response:
        data = await request.data()
        print("DATA", data)
        if data:
            payload = json.loads(str(data, "utf8"))
            return request.returns(payload)
        else:
            return request.returns(True)

    @aon(UPDATE="doc/{cell}/content")
    async def updateCellContent(self, request: Request, cell: str) -> Response:
        data = await request.data()
        print("CONTeNT", cell, data)
        return request.returns("")

    @aon(GET="doc/{cell}/content")
    async def getCellContent(self, request: Request, cell: str) -> Response:
        return request.returns("")


if __name__ == "__main__":
    run(components=[KernelAPI(), ParseAPI(), EditorAPI()], asynchronous=True)
# EOF

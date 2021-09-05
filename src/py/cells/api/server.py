from retro import Request, Response, Component, on, run
from retro.contrib.api import acors


class BlockAPI(Component):

    @on(GET_POST="document")
    async def document(self, request: Request) -> Response:
        data = await request.data()
        print("DATA", data)
        return request.returns(True)


if __name__ == "__main__":
    run(components=[BlockAPI()], asynchronous=True)
# EOF

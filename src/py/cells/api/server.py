from retro import Request, Response, Component, on, run
from retro.contrib.api import setCORSHeaders, acors
from ..parsing.python import Python
import json


class BlockAPI(Component):

    @on(OPTIONS_POST="document")
    @acors()
    async def document(self, request: Request) -> Response:
        data = await request.data()
        print("DATA", data)
        if data:
            payload = json.loads(str(data, "utf8"))
            return request.returns(payload)
        else:
            return request.returns(True)


if __name__ == "__main__":
    run(components=[BlockAPI()], asynchronous=True)
# EOF

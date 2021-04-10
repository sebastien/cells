# TODO: Should say how to import it
from ..kernel import BaseKernel
from typing import List, Any
try:
    import mistune
    # pip3 install - -user - -upgrade mistune == 2.0.0rc1
    assert getattr(mistune, "AstRenderer")
    assert getattr(mistune, "create_markdown")
except Exception as e:
    raise ImportError(
        "Mistune 2.0+ required: python -m pip install --user mistune==2.0.0rc1")

markdown = mistune.create_markdown(renderer=mistune.AstRenderer())
html = mistune.html


class MarkdownKernel(BaseKernel):

    def defineSlot(self, session: str, slot: str):
        pass

    def evalSlot(self,  session: str, slot: str):
        s = self.getSlot(session, slot)
        print("SOURCE", session, slot, s.source)
        return markdown(s.source)

    def renderSlot(self, session: str, slot: str):
        s = self.getSlot(session, slot)
        return html(s.source)

# EOF

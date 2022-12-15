# TODO: Should say how to import it
from ..kernel import BaseKernel
from typing import List

try:
    import mistune

    # pip3 install - -user - -upgrade mistune == 2.0.0rc1
    assert getattr(mistune, "AstRenderer")
    assert getattr(mistune, "create_markdown")
    parseMarkdown = mistune.create_markdown(renderer=mistune.AstRenderer())
    renderMarkdown = mistune.html
except Exception as e:
    # raise ImportError(
    #     "Mistune 2.0+ required: python -m pip install --user mistune==2.0.0rc1"
    # )
    parseMarkdown = lambda _: None
    renderMarkdown = lambda _: None


class MarkdownKernel(BaseKernel):
    def defineSlot(self, session: str, slot: str):
        pass

    def evalSlot(self, session: str, slot: str):
        s = self.getSlot(session, slot)
        return parseMarkdown(s.source)

    def renderSlot(self, session: str, slot: str):
        s = self.getSlot(session, slot)
        return renderMarkdown(s.source)


# EOF

from typing import NamedTuple
import re
import os.path

RE_SEP = re.compile(r"# -- ([A-Z_]+)\n")
RE_DIRECTIVE = re.compile(r"^(\w+): (.+)$")
RE_COMMENT = re.compile(r"\s*#(.*)$")


class Example(NamedTuple):
    inputs: list[str]
    symbols: list[str]
    code: str


def parseExample(text: str) -> Example:
    inputs: list[str] = []
    symbols: list[str] = []
    for line in text.split("\n"):
        if match := RE_COMMENT.match(line):
            comment = match.group(1)
            if match := RE_DIRECTIVE.match(comment):
                value = match.group(2)
                if (group := match.group(1)) == "inputs":
                    inputs = [_.strip() for _ in value.strip().split() if _.strip()]
                elif (group := match.group(1)) == "symbols":
                    symbols = [_.strip() for _ in value.strip().split() if _.strip()]
                else:
                    raise RuntimeError(f"Unsupported directive: {comment}")
    return Example(inputs, symbols, text)


def parseExamples(text: str) -> dict[str, Example]:
    examples: dict[str, list[str]] = {}
    current: list[str] = []
    offset = 0
    for match in RE_SEP.finditer(text):
        current.append(text[offset : match.start()])
        offset = match.end()
        examples[match.group(1)] = current = []
        current.append(text[offset:])
    return {k: parseExample("".join(v)) for k, v in examples.items()}


def loadExample(path: str) -> dict[str, str]:
    # We load the examples for this give
    with open(f"{os.path.dirname(path)}/examples-{os.path.basename(path)}") as f:
        text = f.read()
        examples = {}
        current = []
        offset = 0
        for match in RE_SEP.finditer(text):
            current.append(text[offset : match.start()])
            offset = match.end()
            examples[match.group(1)] = current = []
        current.append(text[offset:])
        return dict((k, "".join(v)) for k, v in examples.items())


# EOF

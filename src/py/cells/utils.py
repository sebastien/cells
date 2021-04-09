import hashlib
from typing import List


def sig(content: List[str]) -> str:
    h = hashlib.sha3_256()
    for _ in content:
        h.update(bytes(_, "utf8"))
    return h.hexdigest()

import hashlib
from typing import List


def sig(content: List[str]) -> str:
    h = hashlib.sha3_256()
    for _ in content:
        h.update(bytes(_, "utf8"))
    return h.hexdigest()


def equal_lines(a: List[str], b: List[str]) -> bool:
    """Tells if both list of strings are identical"""
    if len(a) != len(b):
        return False
    for i, la in enumerate(a):
        if la != b[i]:
            return False
    return True

import hashlib


def sig(content: list[str]) -> str:
    h = hashlib.sha3_256()
    for _ in content:
        h.update(bytes(_, "utf8"))
    return h.hexdigest()


def equal_lines(a: list[str], b: list[str]) -> bool:
    """Tells if both list of strings are identical"""
    if len(a) != len(b):
        return False
    for i, la in enumerate(a):
        if la != b[i]:
            return False
    return True

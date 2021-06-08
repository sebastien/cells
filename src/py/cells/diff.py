from enum import Enum
from collections import OrderedDict
from typing import Union

__doc__ = """
Computes the differences between cells in a document.
"""

# TODO: Should be move-neutral. We really care about having to recompute


class Type(Enum):
    SYMBOL = 0
    NUMBER = 1
    STRING = 2
    LIST = 3
    DICT = 4
    OBJECT = 5


def equalityType(v) -> Type:
    """Returns the equality type of the given object"""
    if v is None:
        return Type.SYMBOL
    elif type(v) in (bool, int, float):
        return Type.NUMBER
    elif isinstance(v, str) or isinstance(v, bytes):
        return Type.STRING
    elif isinstance(v, list) or isinstance(v, tuple):
        return Type.LIST
    elif isinstance(v, dict) or isinstance(v, OrderedDict):
        return Type.DICT
    else:
        return Type.OBJECT


def equalsString(a: Union[str, bytes], b: Union[str, bytes]):
    sa = a if isinstance(a, bytes) else bytes(a, "utf8")
    sb = b if isinstance(b, bytes) else bytes(b, "utf8")
    return sa == sb


def equalsList(a: list, b: list):
    na = len(a)
    nb = len(b)
    if na != nb:
        return False
    for i, v in enumerate(a):
        if not equals(v, b[i]):
            return False
    return True


def equalsDict(a: dict, b: dict):
    checked = []
    for k, v in a.items():
        if k not in b:
            return False
        elif not equals(b[k], v):
            return False
        checked.append(k)
    for k, v in b.items():
        if k in checked:
            continue
        elif k not in a:
            return False
        elif not equals(a[k], v):
            return False
    return True


def equals(a, b) -> bool:
    ta = equalityType(a)
    tb = equalityType(a)
    if ta != tb:
        return False
    elif ta == Type.SYMBOL or ta == Type.NUMBER:
        return ta == tb
    elif ta == Type.STRING:
        return equalsString(a, b)
    elif ta == Type.LIST:
        return equalsList(a, b)
    elif ta == Type.DICT:
        return equalsDict(a, b)
    else:
        return a == b

# EOF

from typing import Optional, List, Dict, ContextManager, Any, Generic, TypeVar, cast
import json

# --
# # Lorem ipsum dolor sit amet
#
# Cras ultricies rhoncus felis, eu sagittis enim pellentesque et. Duis vitae
# turpis nisl. Suspendisse sodales dictum purus et tempus. Morbi accumsan orci
# vitae enim aliquam suscipit. Nullam egestas accumsan euismod. Sed rutrum,
# diam venenatis luctus sollicitudin, ex lectus convallis dui, eget scelerisque
# erat nisl faucibus augue.
#
# Nam vulputate sapien dui, id *sodales tellus convallis* sit amet.
#
# - Vivamus in bibendum neque, nec fringilla ante.
# - Fusce vitae nisi a velit ornare dignissim et eget libero.
# - Sed non nulla eu metus mattis sodales.
#

T = TypeVar("T")

# --
# # Named
#
# `Named` and the `@named` decorator implements base functionality for managing
# named collections.
#
# The `NamedNode` class makes it possible to create named hierarchies.


class Named:

    def __init__(self, name: str):
        self.name: str = name

# A comment that should not be part of the markdown cells content.


def named(obj):
    """Takes an object, goes over its content, and sets the name of any
    `Named` instance to the corresponding slot key."""
    for name, value in ((k, getattr(obj, k)) for k in dir(obj) if isinstance(getattr(obj, k), Named)):
        value.name = value.name or name
    return obj

# EOF

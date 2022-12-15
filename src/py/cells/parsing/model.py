from dataclasses import dataclass
from typing import Optional, Callable, Any


# --
# This defines the `Symbol` and `Scope` clases that are used to capture
# declarations and references in the source code.


@dataclass
class Symbol:
    name: str
    parent: Optional[str] = None
    scope: Optional["Scope"] = None

    # FIXME: Not sure if the range of a symbol is its scope's
    @property
    def range(self) -> tuple[int, int]:
        return self.scope.range if self.scope else (0, 0)

    # FIXME: This is costly so should be cached
    @property
    def inputs(self) -> set:
        refs = set()

        def walk(scope: Scope, depth: int):
            for ref, _ in scope.refs.items():
                if not scope.isDefined(ref):
                    refs.add(ref)

        if self.scope:
            self.scope.walk(walk)
        return refs

    def asDict(self) -> dict[str, Any]:
        return dict(
            name=self.name,
            parent=self.parent,
            range=self.range,
            inputs=[_ for _ in self.inputs],
            scope=self.scope.asDict() if self.scope else None,
        )


class Scope:
    def __init__(self, parent: Optional["Scope"] = None, type: Optional[str] = None):
        self.name: Optional[str] = None
        self.slots: dict[str, str] = {}
        self.refs: dict[str, str] = {}
        self.children: list[Scope] = []
        self.parent: Optional[Scope] = parent
        self.range: tuple[int, int] = (0, 0)
        self.type = type if type else "block"
        if parent:
            parent.children.append(self)

    @property
    def qualname(self) -> Optional[str]:
        parent_name = self.parent.qualname if self.parent else None
        return (
            None
            if not self.name
            else f"{parent_name}.{self.name}"
            if parent_name
            else self.name
        )

    @property
    def defs(self):
        return [_ in self.slots]

    def isDefined(self, name: str) -> bool:
        return self.slots.get(name) == "def" or bool(
            self.parent and self.parent.isDefined(name)
        )

    def derive(
        self,
        type: Optional[str] = None,
        range: Optional[tuple[int, int]] = None,
        name: Optional[str] = None,
    ) -> "Scope":
        res = Scope(self)
        if name:
            res.name = name
        if type:
            res.type = type
        if range:
            res.range = range
        return res

    # FIXME: Not sure this belongs here
    # def walk(self, functor: Callable[[Node, int], None], depth: int = 0):
    #     functor(self, depth)
    #     for _ in self.children:
    #         _.walk(functor, depth + 1)

    def asDict(self) -> dict[str, Any]:
        return dict(
            type=self.type,
            name=self.name,
            qualname=self.qualname,
            range=self.range,
            slots=self.slots,
            refs=self.refs,
            children=[_.asDict() for _ in self.children],
        )

    def __repr__(self) -> str:
        return self.qualname


@dataclass
class Declaration:
    symbol: Symbol


@dataclass
class Reference:
    symbol: Symbol
    scope: Scope


# EOF

import typing as t
from dataclasses import dataclass


@dataclass
class Span:
    start: int
    end: int

    def __add__(self, other: t.Any) -> t.Self:
        if not isinstance(other, Span):
            return NotImplemented

        return self.__class__(start=self.start, end=other.end)


@dataclass
class Spanned[Item]:
    item: Item
    span: Span

    def unpack(self) -> tuple[Item, Span]:
        return self.item, self.span

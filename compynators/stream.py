import typing as t
from dataclasses import dataclass
import os

from compynators.union import Maybe, MaybeType
from compynators.span import Spanned, Span


@dataclass
class Source:
    text: str
    file: os.PathLike[str]

    # TODO: Inefficient
    def line(self, index: int) -> str:
        lines = self.text.splitlines()
        return lines[index]


@dataclass
class Stream[ItemType]:
    file_handle: os.PathLike[str] | None  # TODO: Not a handle
    spans: list[Spanned[ItemType]]
    position: int = 0

    def __iter__(self) -> t.Generator[Spanned[ItemType], None, None]:
        yield from self.spans

    def __len__(self) -> int:
        return len(self.spans)

    @staticmethod
    def from_source(
        source: str, file_handle: os.PathLike[str] | None = None, span_base: int = 0
    ) -> "Stream[str]":
        return Stream(
            file_handle=file_handle,
            spans=[
                Spanned(item, Span(idx, idx + 1))
                for idx, item in enumerate(source, start=span_base)
            ],
        )

    def map[NewItemType](
        self, mapper: t.Callable[[ItemType], NewItemType]
    ) -> "Stream[NewItemType]":
        return Stream(
            file_handle=self.file_handle,
            spans=[
                Spanned(mapper(spanned.item), spanned.span) for spanned in self.spans
            ],
        )

    def remaining(self) -> list[Spanned[ItemType]]:
        return self.spans[self.position :]

    def peek(self) -> MaybeType[Spanned[ItemType]]:
        try:
            span = self.spans[self.position]
        except IndexError:
            return Maybe.Nil
        else:
            return Maybe.Some(span)

    def advance(self, by: int = 1) -> t.Self:
        return self.__class__(
            file_handle=self.file_handle,
            spans=self.spans,
            position=min(self.position + by, len(self.spans)),
        )

    def startswith(self, pattern: t.Sequence[ItemType]) -> bool:
        if len(pattern) == 0:
            return False
        if len(self.spans) < len(pattern):
            return False

        subslice = self.spans[self.position :]
        if len(subslice) == 0:
            return False

        for pat, spanned in zip(pattern, subslice):
            if spanned.item != pat:
                return False

        return True

    def end(self) -> Span:
        return self.spans[-1].span

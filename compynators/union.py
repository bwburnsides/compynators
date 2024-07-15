import typing as t
import typing_extensions as te
from dataclasses import dataclass
from enum import Enum

from compynators.bools import TrueType, FalseType


type MaybeType[T] = Maybe.Some[T] | Maybe.NilType


class Maybe:
    @staticmethod
    def is_some[T](maybe: "MaybeType[T]") -> "te.TypeIs[Maybe.Some[T]]":
        return maybe.is_some()

    @staticmethod
    def is_nil[T](maybe: "MaybeType[T]") -> "te.TypeIs[Maybe.NilType]":
        return maybe.is_nil()

    class NilKind(Enum):
        Nil = 1

        def unwrap(self) -> t.NoReturn:
            assert False, "Unwrapping failed: Maybe.Nil is not Maybe.Some"

        def expect(self, expectation: str) -> t.NoReturn:
            try:
                self.unwrap()
            except AssertionError as exc:
                raise AssertionError(f"Expect failed: {expectation}") from exc

        def __bool__(self) -> bool:
            return False

        def is_some(self) -> FalseType:
            return False

        def is_nil(self) -> "te.TypeIs[Maybe.NilType] | TrueType":
            return True

    @dataclass
    class Some[T]:
        item: T

        def unwrap(self) -> T:
            return self.item

        def expect(self, _expectation: str) -> T:
            return self.item

        def is_some(self) -> "te.TypeIs[Maybe.Some[T]] | TrueType":
            return True

        def is_nil[E](self) -> FalseType:
            return False

    Nil: t.Final[t.Literal[NilKind.Nil]] = NilKind.Nil

    type NilType = t.Literal[NilKind.Nil]


type ResultType[T, E] = Result.Ok[T] | Result.Err[E]


class Result:
    @staticmethod
    def is_ok[T, E](result: "ResultType[T, E]") -> "te.TypeIs[Result.Ok[T]]":
        return result.is_ok()

    @staticmethod
    def is_err[T, E](result: "ResultType[T, E]") -> "te.TypeIs[Result.Err[E]]":
        return result.is_err()

    @dataclass
    class Ok[T]:
        item: T

        def unwrap(self) -> T:
            return self.item

        def unwrap_err(self) -> t.NoReturn:
            assert False, "Unwrapping failed. Result.Ok is not Result.Err"

        def expect(self, _expectation: str) -> T:
            return self.item

        def ok(self) -> MaybeType[T]:
            return Maybe.Some(self.item)

        def and_then[U, E](
            self, op: "t.Callable[[T], ResultType[U, E]]"
        ) -> "ResultType[U, E]":
            return op(self.item)

        def is_ok(self) -> "te.TypeIs[Result.Ok[T]] | TrueType":
            return True

        def is_err[E](self) -> FalseType:
            return False

        def map[U, E](self, func: t.Callable[[T], U]) -> "ResultType[U, E]":
            return Result.Ok(func(self.item))

        def map_or[U, E](self, func: t.Callable[[T], U], default: U) -> U:
            return func(self.item)

        def map_or_else[U, E](
            self, func: t.Callable[[T], U], default: t.Callable[[E], U]
        ) -> U:
            return func(self.item)

        def map_err[E, F](self, func: t.Callable[[E], F]) -> "ResultType[T, F]":
            return self

    @dataclass
    class Err[E]:
        item: E

        def unwrap(self) -> t.NoReturn:
            assert False, "Unwrapping failed. Result.Err is not Result.Ok"

        def unwrap_err(self) -> E:
            return self.item

        def expect(self, expectation: str) -> t.NoReturn:
            try:
                self.unwrap()
            except AssertionError as exc:
                raise AssertionError(f"Expect failed: {expectation}") from exc

        def ok[T](self) -> MaybeType[T]:
            return Maybe.Nil

        def and_then[T, U](
            self, op: "t.Callable[[T], ResultType[U, E]]"
        ) -> "ResultType[U, E]":
            return self

        def is_ok(self) -> FalseType:
            return False

        def is_err(self) -> "te.TypeIs[Result.Err[E]] | TrueType":
            return True

        def map[T, U](self, func: t.Callable[[T], U]) -> "ResultType[U, E]":
            return self

        def map_or[T, U](self, func: t.Callable[[T], U], default: U) -> U:
            return default

        def map_or_else[T, U](
            self, func: t.Callable[[T], U], default: t.Callable[[E], U]
        ) -> U:
            return default(self.item)

        def map_err[T, F](self, func: t.Callable[[E], F]) -> "ResultType[T, F]":
            return Result.Err(func(self.item))

from typing import Iterable, TypeVar, Generator

T = TypeVar("T")


def flatten(iterable: Iterable[Iterable[T]]) -> Generator[T, None, None]:
    for inner in iterable:
        for element in inner:
            yield element

from typing import Iterable, Iterator, Optional, TypeVar, Generator
from os import environ

T = TypeVar("T")


def flatten(iterable: Iterable[Iterable[T]]) -> Generator[T, None, None]:
    for inner in iterable:
        for element in inner:
            yield element


def next_or_none(iterator: Iterator[T]) -> Optional[T]:
    try:
        ret = next(iterator)
    except StopIteration:
        ret = None
    return ret

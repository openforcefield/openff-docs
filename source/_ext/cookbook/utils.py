from functools import partial
from types import FunctionType
from typing import (
    Callable,
    Iterable,
    Iterator,
    Optional,
    TypeVar,
    Generator,
    ParamSpec,
    Union,
)
import contextlib
import os

T = TypeVar("T")
E = TypeVar("E")
P = ParamSpec("P")


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


def _result_inner(fn, exception, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except exception as e:
        return e


def to_result(
    fn: Callable[P, T], exception: type[E] = Exception
) -> Callable[P, Union[T, E]]:
    return partial(_result_inner, fn, exception)


@contextlib.contextmanager
def set_env(**environ):
    """
    Temporarily set the process environment variables.

    >>> with set_env(PLUGINS_DIR='test/plugins'):
    ...   "PLUGINS_DIR" in os.environ
    True

    >>> "PLUGINS_DIR" in os.environ
    False

    :type environ: dict[str, unicode]
    :param environ: Environment variables to set

    From https://stackoverflow.com/a/34333710
    """
    old_environ = dict(os.environ)
    os.environ.update(environ)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_environ)

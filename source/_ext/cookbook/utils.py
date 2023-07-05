from typing import Iterable, TypeVar, Generator
from os import environ

T = TypeVar("T")


def flatten(iterable: Iterable[Iterable[T]]) -> Generator[T, None, None]:
    for inner in iterable:
        for element in inner:
            yield element


def get_cache_prefix(*, default=None) -> str:
    """
    Get the prefix for the cache path - ``main``, ``PR7``, etc

    In RTD, will get the PR number or branch from the environment; otherwise,
    defaults to the cache for the branch given as default. If the default is
    None and the prefix cannot be determined, raises ValueError.
    """
    if environ.get("READTHEDOCS_VERSION_TYPE") == "external":
        return f"PR{environ['READTHEDOCS_VERSION_NAME']}"
    elif "READTHEDOCS_GIT_IDENTIFIER" in environ:
        return environ["READTHEDOCS_GIT_IDENTIFIER"]
    elif default is not None:
        return default
    else:
        raise ValueError("Could not identify cache prefix and default=None")

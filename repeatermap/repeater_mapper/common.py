import contextlib
from abc import ABC, abstractmethod
from typing import Iterator, TextIO, Callable, Iterable

from repeater_mapper import StandardRepeater


@contextlib.contextmanager
def open_urn(urn: str, web_handler: Callable[[str], TextIO]) -> Iterator[TextIO]:
    """

    ..code-block:: python

        with open_urn(filename, web_handler) as csvfile:
            reader = csv.DictReader(csvfile)

    :param urn: a resource name; currently supported: local file names and http(s) scheme.
    :param web_handler: a callable that processes web content and returns the relevant web content as a newline separated TextIO object.
    :return: A contextmanager-wrapped TextIO object providing the resource as lines.
    """
    if urn.startswith("http://") or urn.startswith("https://"):
        yield web_handler(urn)
    else:
        with open(urn, mode="r") as fp:
            yield fp


class AbstractRepeaterReader(ABC):
    @abstractmethod
    def read(self) -> Iterable[StandardRepeater]:
        pass

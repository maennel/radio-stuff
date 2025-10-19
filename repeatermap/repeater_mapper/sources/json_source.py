import json
from typing import Iterable, TextIO

from repeater_mapper import StandardRepeater
from repeater_mapper.common import AbstractRepeaterReader


class JsonRepeaterReader(AbstractRepeaterReader):
    def __init__(self, fd: TextIO):
        self._fd = fd

    def read(self) -> Iterable[StandardRepeater]:
        data = json.load(self._fd)
        for r in data:
            yield StandardRepeater.from_dict(r)

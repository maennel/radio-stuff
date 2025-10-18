from dataclasses import dataclass
from typing import Iterable

from repeater_mapper import StandardRepeater, Band, Status


@dataclass
class RepeaterFilter:
    bands: list[Band]
    status: list[Status]

    def filter(self, repeaters: Iterable[StandardRepeater]) -> Iterable[StandardRepeater]:
        filtered_repeaters = repeaters
        if self.bands:
            filtered_repeaters = filter(lambda r: r.band in self.bands, filtered_repeaters)
        if self.status:
            filtered_repeaters = filter(lambda r: r.status in self.status, filtered_repeaters)
        return filtered_repeaters

    class Builder:
        def __init__(self):
            self._bands = []
            self._status = []

        def bands(self, bands: list[Band]) -> "RepeaterFilter.Builder":
            self._bands = bands
            return self

        def status(self, status: list[Status]) -> "RepeaterFilter.Builder":
            self._status = status
            return self

        def add_band(self, band: Band) -> "RepeaterFilter.Builder":
            self._bands.append(band)
            return self

        def add_status(self, status: Status) -> "RepeaterFilter.Builder":
            self._status.append(status)
            return self

        def build(self) -> "RepeaterFilter":
            return RepeaterFilter(bands=self._bands, status=self._status)

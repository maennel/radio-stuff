from dataclasses import dataclass
from typing import Iterable

from repeater_mapper import StandardRepeater, Band, Status, Area


@dataclass
class RepeaterFilter:
    bands: list[Band]
    status: list[Status]
    areas: list[Area]

    def filter(self, repeaters: Iterable[StandardRepeater]) -> Iterable[StandardRepeater]:
        filtered_repeaters = repeaters
        if self.bands:
            filtered_repeaters = filter(lambda r: r.band in self.bands, filtered_repeaters)
        if self.status:
            filtered_repeaters = filter(lambda r: r.status in self.status, filtered_repeaters)
        if self.areas:
            _list_of_sets = [set(filter(lambda r: area.is_locator_within(r.locator), filtered_repeaters)) for area in
                             self.areas]
            filtered_repeaters = {rep for _set in _list_of_sets for rep in _set}
        return filtered_repeaters

    class Builder:
        def __init__(self):
            self._bands = []
            self._status = []
            self._areas = []

        def bands(self, bands: list[Band]) -> "RepeaterFilter.Builder":
            self._bands = bands
            return self

        def status(self, status: list[Status]) -> "RepeaterFilter.Builder":
            self._status = status
            return self

        def areas(self, areas: list[Area]) -> "RepeaterFilter.Builder":
            self._areas = areas
            return self

        def add_band(self, band: Band) -> "RepeaterFilter.Builder":
            self._bands.append(band)
            return self

        def add_status(self, status: Status) -> "RepeaterFilter.Builder":
            self._status.append(status)
            return self

        def add_area(self, area: Area):
            self._areas.append(area)
            return self

        def build(self) -> "RepeaterFilter":
            return RepeaterFilter(bands=self._bands, status=self._status, areas=self._areas)

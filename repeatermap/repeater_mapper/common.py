import contextlib
from abc import ABC, abstractmethod
from typing import Iterator, TextIO, Callable, Iterable

from repeatermap.repeater_mapper import StandardRepeater


@contextlib.contextmanager
def open_urn(urn: str, web_handler: Callable[[str], TextIO]) -> Iterator[TextIO]:
    if urn.startswith("http://") or urn.startswith("https://"):
        yield web_handler(urn)
    else:
        with open(urn, mode="r") as fp:
            yield fp


class RepeaterPresentation(ABC):
    @abstractmethod
    def write(self, fp: TextIO) -> None:
        pass


class GoogleMapsCSVPresentation(RepeaterPresentation):
    def __init__(self, repeaters: Iterable[StandardRepeater]) -> None:
        self._repeaters = repeaters

    def write(self, fp: TextIO) -> None:
        print("\"Name\",\"Latitude\",\"Longitude\",\"QRG TX\",\"QRG RX\",\"Tone\"", file=fp)
        for r in self._repeaters:
            latlon = r.locator.as_latlon()
            tone = r.nfm.ctcss_tone_tenth_of_hz if r.nfm else None

            print(
                f"\"{r.call} - {r.other_attributes.get('qth', '???')}\","
                f"\"{latlon.lat}\","
                f"\"{latlon.lon}\","
                f"\"{r.qrg_tx_hz / 1_000_000}MHz\","
                f"\"{r.qrg_rx_hz / 1_000_000}MHz\","
                f"\"{str(tone / 10) + "Hz" if tone else ""}\"",
                file=fp
            )

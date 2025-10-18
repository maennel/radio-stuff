import re
from dataclasses import dataclass
from enum import Enum, member
from functools import cached_property, cache
from typing import Optional, Iterable

from pyhamtools.frequency import freq_to_band
from pyhamtools.locator import locator_to_latlong, latlong_to_locator


@dataclass
class Locator:
    value: str

    @cache
    def as_latlon(self) -> "LatLon":
        _sanitized_locator = re.sub('[^a-z0-9]', '', self.value, flags=re.IGNORECASE)
        return LatLon(*locator_to_latlong(_sanitized_locator))

    def __str__(self) -> str:
        return self.value

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass
class LatLon:
    lat: float
    lon: float

    @cache
    def as_locator(self) -> "Locator":
        return Locator(latlong_to_locator(self.lat, self.lon))

    def __str__(self) -> str:
        return f"{self.lat},{self.lon}"

    def __hash__(self) -> int:
        return hash(str(self))


class Status(Enum):
    PLANNED = 0  # Planned
    QRV = 1  # In service
    QRX = 2  # Temporarily deactivated
    QRT = 3  # Turned off


class Band(Enum):
    BAND_10M = 10
    BAND_6M = 6
    BAND_2M = 2
    BAND_70CM = 0.7
    BAND_23CM = 0.23
    BAND_UNKNOWN = None

    @staticmethod
    def from_str(s: str) -> "Band":
        """
        Converts a string, such as "2m" or "70cm" to a Band object.

        :param s: a string expressing the band.
        :return: a Band object.
        """
        if not s.lower().startswith("band_"):
            s = f"band_{s.lower()}"
        try:
            return Band[s.upper()]
        except KeyError:
            raise ValueError(f"{s.upper()} is not a valid Band name.")



    def __str__(self) -> str:
        if self == Band.BAND_UNKNOWN:
            return "???"
        elif float(self.value) < 1.0:
            return f"{int(self.value * 100)}cm"
        else:
            return f"{self.value}m"

    def __hash__(self) -> int:
        return hash(str(self))


@dataclass
class DgId:
    tx: int
    rx: int

    def __str__(self) -> str:
        return f"DG-ID Tx {"%02d" % self.tx} Rx {"%02d" % self.rx}"


class RepeaterCapability:
    pass


@dataclass
class Nfm(RepeaterCapability):
    ctcss_tone_tenth_of_hz: Optional[int] = None  # Continuous Tone Coded Squelch System


@dataclass
class C4FM(RepeaterCapability):
    dg_id: Optional[DgId] = None


@dataclass
class WiresX(RepeaterCapability):
    """
    See https://www.yaesu.com/jp/en/wires-x/id/active_node.php
    """
    node_number: int


@dataclass
class EchoLink(RepeaterCapability):
    node: str


@dataclass
class ToneBurst(RepeaterCapability):
    freq: int


@dataclass
class DMR(RepeaterCapability):
    pass


@dataclass
class DStar(RepeaterCapability):
    pass


@dataclass
class StandardRepeater:
    qrg_tx_hz: int
    qrg_rx_hz: int
    call: str
    locator: Locator
    capabilities: Iterable[RepeaterCapability]
    other_attributes: dict[str, str]
    status: Status

    @cached_property
    def band(self) -> Band:
        try:
            b = freq_to_band(int(self.qrg_tx_hz / 1000))['band']
            return Band(b)
        except KeyError:
            return Band.BAND_UNKNOWN

    @cached_property
    def nfm(self) -> Optional[Nfm]:
        return next(filter(lambda c: isinstance(c, Nfm), self.capabilities), None)

    @cached_property
    def c4fm(self) -> Optional[C4FM]:
        return next(filter(lambda c: isinstance(c, C4FM), self.capabilities), None)

    def as_dict(self) -> dict[str, str | int | bool | dict[str, Optional[str | int]]]:
        d = {
            'qrg_tx_hz': self.qrg_tx_hz,
            'qrg_rx_hz': self.qrg_rx_hz,
            'band': self.band.value,
            'call': self.call,
            'locator': self.locator.value,
            'other_attributes': self.other_attributes,
            'status': self.status.value,
        }
        if self.nfm:
            d['nfm'] = {'tone': self.nfm.ctcss_tone_tenth_of_hz}
        if self.c4fm:
            d['c4fm'] = {
                'tx_dg_id': self.c4fm.dg_id.tx,
                'rx_dg_id': self.c4fm.dg_id.rx,
            } if self.c4fm.dg_id else {}

        return d


def parse_qrg_str(qrg_str: str) -> int:
    """
    Returns a frequency in Hertz.

    :param qrg_str:
    :return:
    """
    return int(float(qrg_str) * 1_000_000)

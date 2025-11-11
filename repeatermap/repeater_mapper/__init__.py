import json
import re
from dataclasses import dataclass
from enum import Enum
from functools import cached_property, cache
from typing import Optional, Iterable

from geopy.distance import geodesic

from repeater_mapper.utils.frequency import freq_to_band
from repeater_mapper.utils.locator import locator_to_latlong, latlong_to_locator


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

    def distance_to(self, other: "LatLon") -> int:
        """Computes the distance in meters between two coordinates in meters."""
        return geodesic((self.lat, self.lon), (other.lat, other.lon)).m

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
class Area:
    center: LatLon
    radius_m: int

    _SEPARATOR = "-"
    _RADIUS_RE = re.compile(r"^(?P<value>[0-9]+)(?P<unit>k?m)$")

    @classmethod
    def from_str(cls, s: str) -> "Area":
        locator, radius_s = s.split(Area._SEPARATOR, maxsplit=1)
        if not (locator and radius_s):
            raise ValueError(f"{s} is not a valid Area expression.")
        return Area.from_locator_radius(Locator(locator), radius_s)

    @staticmethod
    def from_locator_radius(locator: Locator, radius_s: str) -> "Area":
        m = Area._RADIUS_RE.match(radius_s)
        if not m:
            raise ValueError("Could not parse radius value.")

        if m.group("unit") == "km":
            radius_m = int(m.group("value")) * 1000
        else:
            radius_m = int(m.group("value"))
        return Area(center=LatLon(*locator_to_latlong(locator=locator.value)), radius_m=radius_m)

    def __str__(self) -> str:
        return f"{latlong_to_locator(latitude=self.center.lat, longitude=self.center.lon)}{Area._SEPARATOR}{self.radius_m}m"

    def is_locator_within(self, locator: Locator) -> bool:
        return self.is_latlon_within(locator.as_latlon())

    def is_latlon_within(self, latlon: LatLon) -> bool:
        return self.center.distance_to(latlon) <= self.radius_m


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
class DCS(RepeaterCapability):
    """
    Digital Coded Squelch
    """
    code: int
    is_inverted: bool

    def as_zero_padded_string(self) -> str:
        return f'{self.code:03}'

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
            c = freq_to_band(int(self.qrg_rx_hz / 1000))['band']
            if b != c:
                return Band.BAND_UNKNOWN
            return Band(b)
        except ValueError:
            return Band.BAND_UNKNOWN

    @cached_property
    def nfm(self) -> Optional[Nfm]:
        return next(filter(lambda c: isinstance(c, Nfm), self.capabilities), None)

    @cached_property
    def c4fm(self) -> Optional[C4FM]:
        return next(filter(lambda c: isinstance(c, C4FM), self.capabilities), None)

    @cached_property
    def dcs(self) -> Optional[DCS]:
        return next(filter(lambda c: isinstance(c, DCS), self.capabilities), None)

    def as_dict(self) -> dict:
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
        if self.dcs:
            d['dcs'] = {
                "code": self.dcs.code,
                "is_inverted": self.dcs.is_inverted,
            }

        return d

    @classmethod
    def from_dict(cls, d: dict) -> "StandardRepeater":
        capabilities = []
        if 'nfm' in d:
            tone: Optional[int] = None
            if 'tone' in d['nfm']:
                tone = d['nfm']['tone']
            capabilities.append(Nfm(ctcss_tone_tenth_of_hz=tone))
        if 'c4fm' in d:
            dg_id: Optional[DgId] = None
            if len(d['c4fm']) > 0:
                dg_id = DgId(tx=d['c4fm']['tx_dg_id'], rx=d['c4fm']['rx_dg_id'])
            capabilities.append(C4FM(dg_id=dg_id))
        if 'dcs' in d:
            capabilities.append(DCS(**d['dcs']))
        return StandardRepeater(
            qrg_tx_hz=d['qrg_tx_hz'],
            qrg_rx_hz=d['qrg_rx_hz'],
            call=d['call'],
            locator=Locator(d['locator']),
            capabilities=capabilities,
            other_attributes=d['other_attributes'],
            status=Status(d['status']),
        )

    def __hash__(self) -> int:
        return hash(json.dumps(self.as_dict()))


def parse_qrg_str(qrg_str: str) -> int:
    """
    Returns a frequency in Hertz.

    :param qrg_str:
    :return:
    """
    return int(float(qrg_str) * 1_000_000)

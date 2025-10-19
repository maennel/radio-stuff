import csv
from dataclasses import dataclass
from enum import Enum
from functools import cache
from io import StringIO
from typing import TextIO, Iterable, Optional

import requests
from bs4 import BeautifulSoup, NavigableString

from repeater_mapper import StandardRepeater, Locator, Status, Nfm, RepeaterCapability, C4FM, DMR, DStar
from repeater_mapper.common import AbstractRepeaterReader, open_urn

# Found via https://web.r-e-f.org/les-relais-et-balises/
REF_REPEATER_URL = "https://www.r-e-f.org/index.php?option=com_content&view=article&id=1279&Itemid=492"


class TypeStation(Enum):
    RELAIS = "relais"
    BALISE = "balise"


class Etat(Enum):
    PAUSE = "Pause"
    ACTIF = "Actif"
    TEMP = "Temp"
    TEST = "Test"
    PROJET = "Projet"
    ARRET = "Arret"


class Mode(Enum):
    FM = "FM"
    C4FM = "C4FM"
    DMR = "DMR"
    DSTAR = "DSTAR"
    APRS = "APRS"
    ATV = "ATV"
    OTHER = "other"

    @classmethod
    @cache
    def values(cls) -> list[str]:
        return list(map(lambda x: x.value, cls))


@dataclass
class RefRepeater:
    indicatif: str
    station: TypeStation
    etat: Optional[Etat]
    locator: str
    emission_hz: int
    reception_hz: int
    mode: Mode
    ctccs: Optional[int]
    altitude: Optional[str]
    commune: Optional[str]
    url: Optional[str]


class RefWebRepeaterTableReader:
    def read(self, url: str) -> TextIO:
        html = self._read_html(url)

        soup = BeautifulSoup(html, "html.parser")
        main_table = soup.find("table")

        _csv_header = None
        buffer = StringIO("")

        for row in main_table.find_all("tr", recursive=False):
            row_fields = [f for f in row.children if not isinstance(f, NavigableString)]
            if not _csv_header and len(row_fields) > 0 and row_fields[0].name == "th":
                record = [field.text for field in row_fields][1:]
                _csv_header = record
                buffer.write(",".join([f"\"{v}\"" for v in record]))
                buffer.write("\n")

            if (len(row_fields) == 0 or
                (row_fields[0].name != "td") or
                (row_fields[0].name == "td" and "class" not in row_fields[0].attrs) or
                (row_fields[0].name == "td" and row_fields[0]["class"] != ["droite", "rose"])
            ):
                continue

            # Leave away first record as it's always empty
            record = []
            i = 0
            for field in row_fields[1:]:
                value = field.text
                if field.a and i!=0:
                    value = field.a.attrs["href"]
                i+=1
                record.append(value)
            buffer.write(",".join([f"\"{v}\"" for v in record]))
            buffer.write("\n")

        buffer.seek(0)
        return buffer

    @staticmethod
    def _read_html(url: str) -> str:
        r = requests.get(url)
        return r.text


class Parser:
    def __init__(self, url: str):
        self._url = url
        self._web_repeater_table_reader = RefWebRepeaterTableReader()

    def parse(self) -> Iterable[RefRepeater]:
        with open_urn(self._url, self._web_repeater_table_reader.read) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                emission_hz = int(float(row["émission"]
                                        .replace("MHz", "")
                                        .strip()
                                        .replace("\xa0", "")
                                        .replace(",", ".")
                                        ) * 1_000_000
                                  ) if row["émission"] else None
                reception_hz = int(float(row["réception"]
                                         .replace("MHz", "")
                                         .strip()
                                         .replace("\xa0", "")
                                         .replace(",", ".")
                                         ) * 1_000_000
                                   ) if row["réception"] else None
                ctccs_tenths_of_hz = int(float(row["ctccs"]
                                               .replace("Hz", "")
                                               .strip()
                                               .replace("\xa0", "")
                                               .replace(",", ".")
                                               ) * 10
                                         ) if row["ctccs"] else None
                if any([emission_hz is None, reception_hz is None]):
                    # Skip systems for which we don't know the frequency.
                    continue
                yield RefRepeater(
                    indicatif=row["indicatif"],
                    station=TypeStation(row["station"]),
                    etat=Etat(row["état"].strip()) if row["état"] else None,
                    locator=row["Locator"],
                    emission_hz=emission_hz,
                    reception_hz=reception_hz,
                    mode=Mode(row["mode"]) if row["mode"] in Mode.values() else Mode.OTHER,
                    ctccs=ctccs_tenths_of_hz,
                    altitude= row["altitude"].replace("\xa0", ""),
                    commune= row["commune"],
                    url=row["url"].strip().replace("http://", "https://") if bool(row["url"]) else None,
                )


class Converter:
    def convert(self, repeater: RefRepeater) -> StandardRepeater:
        mode_map: dict[Mode, RepeaterCapability] = {
            Mode.FM: Nfm(ctcss_tone_tenth_of_hz=repeater.ctccs),
            Mode.C4FM: C4FM(dg_id=None),
            Mode.DMR: DMR(),
            Mode.DSTAR: DStar(),
        }
        capabilities = [mode_map[repeater.mode]] if repeater.mode in mode_map else []
        status_map = {
            Etat.PROJET: Status.PLANNED,
            Etat.ACTIF: Status.QRV,
            Etat.TEST: Status.QRV,
            Etat.TEMP: Status.QRV,
            Etat.PAUSE: Status.QRX,
            Etat.ARRET: Status.QRT,
        }
        other_attributes = {}
        if repeater.altitude:
            other_attributes["altitude"] = repeater.altitude
        if repeater.commune:
            other_attributes["qth"] = repeater.commune
        if repeater.url:
            other_attributes["url"] = repeater.url
        return StandardRepeater(
            qrg_tx_hz=repeater.emission_hz,
            qrg_rx_hz=repeater.reception_hz,
            call=repeater.indicatif,
            locator=Locator(repeater.locator),
            capabilities=capabilities,
            other_attributes=other_attributes,
            status=status_map[repeater.etat] if repeater.etat else Status.QRV,
        )


class RefRepeaterReader(AbstractRepeaterReader):
    def __init__(self, data_source: str = REF_REPEATER_URL):
        self._data_source = data_source
        self._converter = Converter()
        self._parser = Parser(data_source)

    def read(self) -> Iterable[StandardRepeater]:
        ref_repeaters = self._parser.parse()
        for r in ref_repeaters:
            if r.station != TypeStation.RELAIS:
                continue
            yield self._converter.convert(r)


if __name__ == '__main__':
    for r in RefRepeaterReader().read():
        print(r)

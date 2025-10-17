import csv
import re
import sys
from dataclasses import dataclass
from enum import Enum
from io import StringIO
from typing import Iterable, TextIO

import requests
from bs4 import BeautifulSoup

from repeatermap.repeater_mapper import Locator, parse_qrg_str, StandardRepeater, RepeaterCapability, Nfm, C4FM, \
    EchoLink, Status, Band
from repeatermap.repeater_mapper.common import open_urn, GoogleMapsCSVPresentation


class UskaStatus(Enum):
    PLANNED = 0  # Planned
    QRV = 1  # In service
    QRX = 2  # Temporarily deactivated
    QRT = 3  # Turned off


# Define the Repeater class
@dataclass
class UskaRepeater:
    qrg_tx_hz: int
    qrg_rx_hz: int
    call: str
    qth: str
    kanton: str
    locator: Locator
    alt_m: int
    remarks: str
    status: UskaStatus


class UskaWebRepeaterTableReader:
    def read(self, url: str) -> TextIO:
        html = self._read_html(url)

        soup = BeautifulSoup(html, "html.parser")
        repeater_table = soup.find("table", id=re.compile("^tablepress"))

        buffer = StringIO("")

        # Read table header
        header_tags = repeater_table.find("thead").find("tr").find_all("th")
        field_names = []
        for column in header_tags:
            field_names.append(column.text)
        buffer.write(",".join([f"\"{f}\"" for f in field_names]))
        buffer.write("\n")

        # Read repeater data
        data_table = repeater_table.find("tbody").find_all("tr")
        for row in data_table:
            row_values = []
            for column in row.find_all("td"):
                row_values.append(column.text)
            buffer.write(",".join([f"\"{v}\"" for v in row_values]))
            buffer.write("\n")

        buffer.seek(0)
        return buffer

    @staticmethod
    def _read_html(url: str) -> str:
        r = requests.get(url)
        return r.text


class Parser:
    def __init__(self, filename):
        self._filename = filename
        self._web_repeater_table_reader = UskaWebRepeaterTableReader()

    def parse(self) -> Iterable[UskaRepeater]:
        """Parse the table data into a list of Repeater objects"""
        with open_urn(self._filename, self._web_repeater_table_reader.read) as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                try:
                    qrg_tx_hz = parse_qrg_str(row['QRG TX'])
                    qrg_rx_hz = parse_qrg_str(row['QRG RX'])
                    yield UskaRepeater(
                        qrg_tx_hz=qrg_tx_hz,
                        qrg_rx_hz=qrg_rx_hz,
                        call=row["Call"],
                        qth=row["QTH"],
                        kanton=row["Kanton"],
                        locator=Locator(row["Locator"]),
                        alt_m=int(row["Alt. m"]),
                        remarks=row["Remarks"],
                        status=UskaStatus(int(row["Status"]))
                    )
                except ValueError as e:
                    print(f"Could not parse {row}: {e}")
                    print("Skipping...")


class Converter:
    _NFM = re.compile('(^FM|[N ]FM)')
    _CTCSS_TONE = re.compile('T(?P<freq>[0-9]{2,3}.[0-9])')
    _C4FM = re.compile('C4(?:FM)?')
    _ECHO_LINK = re.compile('EL#?(?P<node>[0-9]{5,6})')

    def convert(self, repeater: UskaRepeater) -> StandardRepeater:
        return StandardRepeater(
            qrg_tx_hz=repeater.qrg_tx_hz,
            qrg_rx_hz=repeater.qrg_rx_hz,
            call=repeater.call,
            locator=repeater.locator,
            capabilities=self._parse_capabilities(repeater.remarks),
            other_attributes={
                'original_remarks': repeater.remarks,
                'canton': repeater.kanton,
                'alt_m': repeater.alt_m,
                'qth': repeater.qth,
            },
            status=Status(repeater.status.value),
        )

    def _parse_capabilities(self, remarks: str) -> Iterable[RepeaterCapability]:
        _capabilities = list()
        _nfm = self._NFM.search(remarks)
        _ctcss = self._CTCSS_TONE.search(remarks)
        _c4fm = self._C4FM.search(remarks)
        _echo_link = self._ECHO_LINK.search(remarks)
        if _nfm:
            if _ctcss:
                _capabilities.append(Nfm(ctcss_tone_tenth_of_hz=int(float(_ctcss.group("freq")) * 10)))
            else:
                _capabilities.append(Nfm())
        if _c4fm:
            _capabilities.append(C4FM(dg_id=None))
        if _echo_link:
            _capabilities.append(EchoLink(node=_echo_link.group('node')))
        return _capabilities




def main(data_source: str) -> None:
    converter = Converter()
    uska_repeaters = Parser(data_source).parse()
    std_repeaters = [converter.convert(r) for r in uska_repeaters]

    for band in [Band.BAND_2M, Band.BAND_70CM]:
        band_repeaters = filter(lambda r: r.status == Status.QRV and r.band == band, std_repeaters)
        presentation = GoogleMapsCSVPresentation(band_repeaters)
        print(f"### Repeaters on {band} ###")
        presentation.write(sys.stdout)

    # TODO: Create Google Map with all repeaters.
    # TODO: Store current list in machine parseable format.

if __name__ == "__main__":
    # main("../HB Repeater-Voice List.csv")
    main("https://uska.ch/hb-repeater-voice-list/")

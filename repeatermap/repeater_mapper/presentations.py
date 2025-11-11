import csv
import json
import sys
from abc import ABC, abstractmethod
from typing import TextIO, Iterable

from repeater_mapper import StandardRepeater
from repeater_mapper.utils import CHAR_TRANSLATION_TABLE


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
            repeater_name = f"{r.call} - {r.other_attributes.get('qth', '???')}"
            try:
                latlon = r.locator.as_latlon()
            except ValueError:
                print(f"Could not convert locator \"{r.locator}\" to lat/lon format. Skipping \"{repeater_name}\".", file=sys.stderr)
            tone = r.nfm.ctcss_tone_tenth_of_hz if r.nfm else None

            print(
                f"\"{repeater_name}\","
                f"\"{latlon.lat}\","
                f"\"{latlon.lon}\","
                f"\"{r.qrg_tx_hz / 1_000_000}MHz\","
                f"\"{r.qrg_rx_hz / 1_000_000}MHz\","
                f"\"{str(tone / 10) + "Hz" if tone else ""}\"",
                file=fp
            )


class YaesuFt5deAdms14CsvPresentation(RepeaterPresentation):
    _ACCEPTED_TONE_FREQS: list[int] = [
        670,
        693,
        719,
        744,
        770,
        797,
        825,
        854,
        885,
        915,
        948,
        974,
        1000,
        1035,
        1072,
        1109,
        1148,
        1188,
        1230,
        1273,
        1318,
        1365,
        1413,
        1462,
        1500,
        1514,
        1567,
        1598,
        1622,
        1655,
        1679,
        1713,
        1738,
        1773,
        1799,
        1835,
        1862,
        1899,
        1928,
        1966,
        1995,
        2035,
        2065,
        2107,
        2181,
        2257,
        2291,
        2336,
        2418,
        2503,
        2541,
    ]
    _FIELD_NAMES: list[str] = [
        "Channel No",
        "Priority CH",
        "Rx Freq",
        "Tx Freq",
        "Offset Freq",
        "Offset Direction",
        "Auto Mode",
        "Operating Mode",
        "DIG/ANALOG",
        "TAG",
        "Name",
        "Tone Mode",
        "CTCSS Freq",
        "DCS Code",
        "DCS Polarity",
        "User CTCSS",
        "RX DG-ID",
        "TX DG-ID",
        "Tx Power",
        "Skip",
        "AUTO STEP",
        "Step",
        "Memory Mask",
        "ATT",
        "S-Meter SQL",
        "Bell",
        "Narrow",
        "Clock Shift",
        "BANK 1",
        "BANK 2",
        "BANK 3",
        "BANK 4",
        "BANK 5",
        "BANK 6",
        "BANK 7",
        "BANK 8",
        "BANK 9",
        "BANK 10",
        "BANK 11",
        "BANK 12",
        "BANK 13",
        "BANK 14",
        "BANK 15",
        "BANK 16",
        "BANK 17",
        "BANK 18",
        "BANK 19",
        "BANK 20",
        "BANK 21",
        "BANK 22",
        "BANK 23",
        "BANK 24",
        "Comment",
        "Suffix",
    ]

    def __init__(self, repeaters: Iterable[StandardRepeater]) -> None:
        self._repeaters = repeaters

    def write(self, fp: TextIO) -> None:
        self._writer = csv.DictWriter(fp, fieldnames=self._FIELD_NAMES, delimiter=",", quoting=csv.QUOTE_NONE)
        counter = 0
        for r in self._repeaters:
            counter += 1
            row = self._convert_to_csv_row(counter, r)
            self._writer.writerow(row)
        while counter < 900:
            counter += 1
            row = self._get_padding_row(counter)
            self._writer.writerow(row)


    def _convert_to_csv_row(self, i: int, r: StandardRepeater) -> dict[str, str | int]:
        freq_offset = r.qrg_tx_hz - r.qrg_rx_hz
        if freq_offset == 0:
            offset_direction = "OFF"
        elif freq_offset < 0:
            offset_direction = "+RPT"
        else:
            offset_direction = "-RPT"

        if not r.nfm and r.c4fm:
            mode_switching = "DN"  # Digital (C4FM) only
        elif r.nfm and not r.c4fm:
            mode_switching = "FM"
        else: #    if r.nfm and r.c4fm:
            mode_switching = "AMS"  # Automated Mode Switch

        tone_mode = "OFF"
        ctcss_freq = self._ACCEPTED_TONE_FREQS[0]
        dcs_code = "023"
        dcs_polarity = "RX Normal TX Normal"

        if r.nfm and r.nfm.ctcss_tone_tenth_of_hz:
            tone_mode: str = "TONE"
            ctcss_freq: int = r.nfm.ctcss_tone_tenth_of_hz
            if ctcss_freq not in self._ACCEPTED_TONE_FREQS:
                diffs = [abs(r.nfm.ctcss_tone_tenth_of_hz - t) for t in self._ACCEPTED_TONE_FREQS]
                index = diffs.index(min(diffs))
                ctcss_freq = self._ACCEPTED_TONE_FREQS[index]
        elif r.dcs:
            tone_mode = "DCS"
            dcs_code = r.dcs.as_zero_padded_string()
            dcs_polarity = "RX Invert TX Invert" if r.dcs.is_inverted else "RX Normal TX Normal"

        name_long = f"{r.call.replace("HB9", "", 1)} {r.other_attributes.get('qth', '???').translate(CHAR_TRANSLATION_TABLE)}"
        return {
            "Channel No": i,
            "Priority CH": "OFF",
            "Rx Freq": r.qrg_tx_hz / 1_000_000,  # Tx freq of the repeater is the Rx freq of the radio
            "Tx Freq": r.qrg_rx_hz / 1_000_000,  # ...and vice versa
            "Offset Freq": abs(freq_offset) / 1_000_000,
            "Offset Direction": offset_direction,
            "Auto Mode": "ON",
            "Operating Mode": "FM",
            "DIG/ANALOG": mode_switching,
            "TAG": "ON",
            "Name": name_long[:16].rstrip(" /.,-"),
            "Tone Mode": tone_mode,
            "CTCSS Freq": f"{ctcss_freq / 10} Hz",
            "DCS Code": dcs_code,
            "DCS Polarity": dcs_polarity,
            "User CTCSS": "1600 Hz",
            "RX DG-ID": "RX 00",
            "TX DG-ID": "TX 00",
            "Tx Power": "High (5W)",
            "Skip": "OFF",
            "AUTO STEP": "ON",
            "Step": "6.25KHz",
            "Memory Mask": "OFF",
            "ATT": "OFF",
            "S-Meter SQL": "OFF",
            "Bell": "OFF",
            "Narrow": "OFF",
            "Clock Shift": "OFF",
            "BANK 1": "OFF",
            "BANK 2": "OFF",
            "BANK 3": "OFF",
            "BANK 4": "OFF",
            "BANK 5": "OFF",
            "BANK 6": "OFF",
            "BANK 7": "OFF",
            "BANK 8": "OFF",
            "BANK 9": "OFF",
            "BANK 10": "OFF",
            "BANK 11": "OFF",
            "BANK 12": "OFF",
            "BANK 13": "OFF",
            "BANK 14": "OFF",
            "BANK 15": "OFF",
            "BANK 16": "OFF",
            "BANK 17": "OFF",
            "BANK 18": "OFF",
            "BANK 19": "OFF",
            "BANK 20": "OFF",
            "BANK 21": "OFF",
            "BANK 22": "OFF",
            "BANK 23": "OFF",
            "BANK 24": "OFF",
            "Comment": "",
            "Suffix": "0",
        }

    @staticmethod
    def _get_padding_row(i: int) -> dict[str, str | int]:
        return {
            "Channel No": i,
            "Priority CH": "",
            "Rx Freq": "",
            "Tx Freq": "",
            "Offset Freq": "",
            "Offset Direction": "",
            "Auto Mode": "",
            "Operating Mode": "",
            "DIG/ANALOG": "",
            "TAG": "",
            "Name": "",
            "Tone Mode": "",
            "CTCSS Freq": "",
            "DCS Code": "",
            "DCS Polarity": "",
            "User CTCSS": "",
            "RX DG-ID": "",
            "TX DG-ID": "",
            "Tx Power": "",
            "Skip": "",
            "AUTO STEP": "",
            "Step": "",
            "Memory Mask": "",
            "ATT": "",
            "S-Meter SQL": "",
            "Bell": "",
            "Narrow": "",
            "Clock Shift": "",
            "BANK 1": "",
            "BANK 2": "",
            "BANK 3": "",
            "BANK 4": "",
            "BANK 5": "",
            "BANK 6": "",
            "BANK 7": "",
            "BANK 8": "",
            "BANK 9": "",
            "BANK 10": "",
            "BANK 11": "",
            "BANK 12": "",
            "BANK 13": "",
            "BANK 14": "",
            "BANK 15": "",
            "BANK 16": "",
            "BANK 17": "",
            "BANK 18": "",
            "BANK 19": "",
            "BANK 20": "",
            "BANK 21": "",
            "BANK 22": "",
            "BANK 23": "",
            "BANK 24": "",
            "Comment": "",
            "Suffix": "0",
        }

class JsonPresentation(RepeaterPresentation):
    def __init__(self, repeaters: Iterable[StandardRepeater]) -> None:
        self._repeaters = repeaters

    def write(self, fp: TextIO) -> None:
        json.dump([r.as_dict() for r in self._repeaters], fp, indent=2, separators=(",", ":"))


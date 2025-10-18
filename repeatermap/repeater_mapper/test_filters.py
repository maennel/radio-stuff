from unittest import TestCase

from repeater_mapper import Status, Band, StandardRepeater
from repeater_mapper.filters import RepeaterFilter


class TestRepeaterFilter(TestCase):
    REPEATER_FIXTURES = [
        StandardRepeater(
            qrg_tx_hz=144_500_000,
            qrg_rx_hz=144_500_000,
            call="HB9TEST1",
            locator="JN41AA",
            capabilities=[],
            other_attributes={},
            status=Status.QRV
        ),
        StandardRepeater(
            qrg_tx_hz=144_500_000,
            qrg_rx_hz=144_500_000,
            call="HB9TEST2",
            locator="JN41AA",
            capabilities=[],
            other_attributes={},
            status=Status.QRT
        ),
        StandardRepeater(
            qrg_tx_hz=435_000_000,
            qrg_rx_hz=435_000_000,
            call="HB9TEST3",
            locator="JN41AA",
            capabilities=[],
            other_attributes={},
            status=Status.QRV
        ),
    ]

    def test_filter_w_bands_status(self):
        _filter = RepeaterFilter(bands=[Band.BAND_2M], status=[Status.QRV])
        filtered_repeaters = list(_filter.filter(self.REPEATER_FIXTURES))
        self.assertEqual(["HB9TEST1"], [r.call for r in filtered_repeaters])

    def test_filter_w_bands_only(self):
        _filter = RepeaterFilter(bands=[Band.BAND_2M], status=[])
        filtered_repeaters = list(_filter.filter(self.REPEATER_FIXTURES))
        self.assertEqual(["HB9TEST1", "HB9TEST2"], [r.call for r in filtered_repeaters])

    def test_filter_w_status_only(self):
        _filter = RepeaterFilter(bands=[], status=[Status.QRV])
        filtered_repeaters = list(_filter.filter(self.REPEATER_FIXTURES))
        self.assertEqual(["HB9TEST1", "HB9TEST3"], [r.call for r in filtered_repeaters])

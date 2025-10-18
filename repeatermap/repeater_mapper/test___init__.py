from unittest import TestCase

from repeater_mapper import LatLon, Locator, StandardRepeater, Nfm, Status, C4FM, DgId


class TestLatLon(TestCase):
    def test_as_locator(self):
        locator = LatLon(0.0, 0.0).as_locator()
        latlon = locator.as_latlon()
        self.assertEqual(Locator("JJ00AA"), locator)
        self.assertGreater(0.05, abs(latlon.lat))
        self.assertGreater(0.05, abs(latlon.lon))


class TestAsDict(TestCase):
    def test_as_dict_with_single_nfm(self):
        r = StandardRepeater(
            qrg_tx_hz=145650000,
            qrg_rx_hz=145050000,
            call="HB0TEST",
            locator=LatLon(0.0, 0.0).as_locator(),
            capabilities=[
                Nfm(ctcss_tone_tenth_of_hz=670),
            ],
            other_attributes={},
            status=Status.QRV,
        )
        d = r.as_dict()
        self.assertDictEqual(d, {
            'qrg_tx_hz': 145650000,
            'qrg_rx_hz': 145050000,
            'band': 2,
            'call': 'HB0TEST',
            'locator': 'JJ00AA',
            'other_attributes': {},
            'status': 1,
            'nfm': {'tone': 670},
        })

    def test_as_dict_with_no_nfm(self):
        r = StandardRepeater(
            qrg_tx_hz=145650000,
            qrg_rx_hz=145050000,
            call="HB0TEST",
            locator=LatLon(0.0, 0.0).as_locator(),
            capabilities=[],
            other_attributes={},
            status=Status.QRV,
        )
        d = r.as_dict()
        self.assertDictEqual(d, {
            'qrg_tx_hz': 145650000,
            'qrg_rx_hz': 145050000,
            'band': 2,
            'call': 'HB0TEST',
            'locator': 'JJ00AA',
            'status': 1,
            'other_attributes': {},
        })

    def test_as_dict_with_multiple_nfm(self):
        r = StandardRepeater(
            qrg_tx_hz=145_650_000,
            qrg_rx_hz=145_050_000,
            call="HB0TEST",
            locator=LatLon(0.0, 0.0).as_locator(),
            capabilities=[
                Nfm(ctcss_tone_tenth_of_hz=670),
                Nfm(ctcss_tone_tenth_of_hz=719),
            ],
            other_attributes={},
            status=Status.QRV,
        )
        d = r.as_dict()
        self.assertDictEqual(d, {
            'qrg_tx_hz': 145_650_000,
            'qrg_rx_hz': 145_050_000,
            'band': 2,
            'call': 'HB0TEST',
            'locator': 'JJ00AA',
            'other_attributes': {},
            'status': 1,
            'nfm': {'tone': 670},
        })

    def test_as_dict_with_c4fm(self):
        r = StandardRepeater(
            qrg_tx_hz=145_650_000,
            qrg_rx_hz=145_050_000,
            call="HB0TEST",
            locator=LatLon(0.0, 0.0).as_locator(),
            capabilities=[
                C4FM(dg_id=DgId(tx=1, rx=2)),
            ],
            other_attributes={},
            status=Status.QRV,
        )
        d = r.as_dict()
        self.assertDictEqual(d, {
            'qrg_tx_hz': 145_650_000,
            'qrg_rx_hz': 145_050_000,
            'band': 2,
            'call': 'HB0TEST',
            'locator': 'JJ00AA',
            'other_attributes': {},
            'status': 1,
            'c4fm': {'tx_dg_id': 1, 'rx_dg_id': 2},
        })

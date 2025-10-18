from unittest import TestCase

from repeater_mapper.utils import CHAR_TRANSLATION_TABLE


class TestCharTranslationTable(TestCase):

    def test_char_translation_table(self):
        self.assertEqual("aeoeue", "äöü".translate(CHAR_TRANSLATION_TABLE))
        self.assertEqual("Laegern", "Lägern".translate(CHAR_TRANSLATION_TABLE))
        self.assertEqual("Chateau-dOeux", "Château-d'Oeux".translate(CHAR_TRANSLATION_TABLE))

#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Test the apographe.languages_and_scripts module
"""

from apographe.languages_and_scripts import is_latn, romanize


class TestIsLatin:
    def test_all(self):
        assert is_latn("bei jing shi")
        assert is_latn("Bei Jing Shi")
        assert is_latn("bei jing")
        assert is_latn("Bei Jing")
        assert is_latn("bei3jing1")
        assert is_latn("bei3jing1shi4")
        assert is_latn("běijīng")
        assert is_latn("běijīng")
        assert is_latn("běijīngshì")
        assert is_latn("běijīngshì")
        assert is_latn("Miliana")
        assert is_latn("Pekin")
        assert is_latn("Pékin")
        assert is_latn("Peking")
        assert is_latn("Pekino")
        assert is_latn("Pekíno")
        assert is_latn("Pekíno")
        assert is_latn("Zucchabar")


class TestRomanize:
    def test_arab(self):
        s = "بكين"
        romanizations = romanize(s)
        assert romanizations == {"bkyn"}

    def test_cyrl(self):
        s = "Пекин"
        romanizations = romanize(s, "ru")
        assert romanizations == {"Pekin", "Pekine", "Pekyn"}
        s = "Пекинг"
        romanizations = romanize(s, "sr")
        assert romanizations == {"Peking", "Pekyng"}

    def test_grek(self):
        s = "Πεκίνο"
        romanizations = romanize(s)
        assert romanizations == {"Pekino", "Pekíno", "Pekíno"}

    def test_hani(self):
        s = "北京"
        romanizations = romanize(s)
        assert romanizations == {
            "bei3jing1",
            "běijīng",
            "Bei Jing",
            "bei jing",
            "běijīng",
        }
        s = "北京市"
        romanizations = romanize(s)
        assert romanizations == {
            "bei jing shi",
            "Bei Jing Shi",
            "běijīngshì",
            "bei3jing1shi4",
            "běijīngshì",
        }

    def test_latn(self):
        s = "Beijing"
        romanizations = romanize(s)
        assert romanizations == {s}
        s = "Pékin"
        romanizations = romanize(s)
        assert romanizations == {s, "Pekin", "Pékin"}

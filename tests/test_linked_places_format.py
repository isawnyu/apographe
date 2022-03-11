#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Test the apographe.linked_places_format module
"""
from apographe.linked_places_format import Properties


class TestProperties:
    def test_defaults(self):
        p = Properties()
        assert p.title == ""
        assert p.ccodes == list()

    def test_ccodes(self):
        p = Properties(ccodes=["GB"])
        assert p.ccodes == ["GB"]
        p = Properties(ccodes=["GB", "ESP"])
        assert set(p.ccodes) == {"GB", "ES"}  # NB substitution of preferred form
        p = Properties(ccodes=["Mexico"])
        assert p.ccodes == ["MX"]

    def test_titles(self):
        p = Properties(title="Moontown")
        assert p.title == "Moontown"
        p.title = "Brownsboro"
        assert p.title == "Brownsboro"
        p.title = "    \t"
        assert p.title == ""

#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Test the apographe.linked_places_format module
"""
from apographe.linked_places_format import Feature, Properties
import pytest


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
        assert set(p.country_names) == {
            "Spain",
            "United Kingdom of Great Britain and Northern Ireland",
        }
        p.remove_ccode("ES")
        assert p.ccodes == ["GB"]
        p = Properties(ccodes=["Mexico"])
        assert p.ccodes == ["MX"]
        p.remove_ccode("Mexico")
        with pytest.raises(KeyError):
            p.remove_ccode("Narnia")

    def test_titles(self):
        p = Properties(title="Moontown")
        assert p.title == "Moontown"
        p.title = "Brownsboro"
        assert p.title == "Brownsboro"
        p.title = "    \t"
        assert p.title == ""


class TestFeature:
    def test_defaults(self):
        f = Feature()
        assert f.id is None
        assert f.uri is None
        assert isinstance(f.internal_id, str)

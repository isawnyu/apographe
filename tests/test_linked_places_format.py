#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Test the apographe.linked_places_format module
"""
from apographe.linked_places_format import Feature, Name, Properties
import logging
import pytest
import re
from uuid import UUID


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

    def test_ids(self):
        id = "fish001"
        f = Feature(id=id)
        assert f.id == id
        id = "banana-junior-2000"
        f.id = id
        assert f.id == id

    def test_internal_ids(self):
        f = Feature()
        hex = f.internal_id
        rx = re.compile(r"^[0-9a-f]{32}$")
        assert rx.match(hex)
        UUID(hex)

    def test_uris(self):
        uri = "https://pleiades.stoa.org/places/12345/json"
        f = Feature(uri=uri)
        assert f.uri == uri
        uri = "https://edh.ub.uni-heidelberg.de/edh/geographie/G013662/json"
        f.uri = uri
        assert f.uri == uri
        uri = "https:// 1 bad web uri"
        with pytest.raises(ValueError):
            f.uri = uri


class TestName:
    def test_lang(self):
        n = Name()
        assert n.lang == "und"
        n = Name(lang="en-Arab-US")
        assert n.lang == "en-Arab-US"
        assert n.language_subtag == "en"
        assert n.region_subtag == "US"
        assert n.script_subtag == "Arab"
        n.lang = "en"
        assert n.lang == "en"
        assert n.language_subtag == "en"
        assert n.region_subtag is None
        assert n.script_subtag == "Latn"
        n.lang = "grc"
        assert n.lang == "grc"
        assert n.language_subtag == "grc"
        assert n.region_subtag is None
        assert (
            n.script_subtag is None
        )  # sadly, this is what the IANA registry says: no default script for "grc"

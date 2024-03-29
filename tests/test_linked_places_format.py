#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Test the apographe.linked_places_format module
"""
from apographe.linked_places_format import Feature, Name, NameCollection, Properties
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

    def test_name_collection(self):
        f = Feature(names=[Name("foo"), Name("bar")])
        assert isinstance(f.names, NameCollection)
        assert len(f.names) == 2
        for n in f.names:
            assert isinstance(n, Name)
        assert set([n.toponym for n in f.names]) == {"foo", "bar"}
        names = f.names.get_names("foo")
        f.names.remove_name(names[0])
        assert set([n.toponym for n in f.names]) == {"bar"}
        names = f.names.get_names("bar")
        f.names.remove_name(names[0])
        assert len(f.names) == 0


class TestName:
    def test_lang(self):
        n = Name()
        assert n.language_tag == "und"
        n = Name(language_tag="en-Arab-US")
        assert n.language_tag == "en-Arab-US"
        assert n.language_subtag == "en"
        assert n.region_subtag == "US"
        assert n.script_subtag == "Arab"
        n.language_tag = "en"
        assert n.language_tag == "en"
        assert n.language_subtag == "en"
        assert n.region_subtag is None
        assert n.script_subtag == "Latn"
        n.language_tag = "grc"
        assert n.language_tag == "grc"
        assert n.language_subtag == "grc"
        assert n.region_subtag is None
        assert (
            n.script_subtag is None
        )  # sadly, this is what the IANA registry says: no default script for "grc"

    def test_romanizations(self):
        n = Name(romanizations=("foo", "phō"))
        assert set(n.romanizations) == {"foo", "phō"}

    def test_toponym(self):
        n = Name(toponym="foo")
        assert n.toponym == "foo"
        n.toponym = "bar"
        assert n.toponym == "bar"
        del n.toponym
        assert n.toponym is None


class TestNameCollection:
    def test_name_collection(self):
        names = [Name("foo"), Name("bar")]
        nc = NameCollection(names=names)
        assert len(nc) == 2
        names = nc.get_names("foo")
        assert len(names) == 1
        assert names[0].toponym == "foo"
        names = nc.get_names("Foo")
        assert len(names) == 1
        assert names[0].toponym == "foo"
        nc.add_name(Name("Shoo"))
        nc.add_name(Name("Shoe"))
        assert len(nc) == 4
        names = nc.get_names("oo")
        assert len(names) == 2
        assert set([n.toponym for n in names]) == {"foo", "Shoo"}
        for n in names:
            nc.remove_name(n)
        assert len(nc) == 2
        assert set([n.toponym for n in nc.names]) == {"bar", "Shoe"}
        names = nc.get_names("bar")
        assert len(names) == 1
        assert names[0].toponym == "bar"

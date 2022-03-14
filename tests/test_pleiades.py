#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Test the apographe.pleiades module
"""

from apographe.pleiades import Pleiades, PleiadesQuery
from apographe.serialization import ApographeEncoder
from apographe.web import BackendWeb
import geojson
import json
import logging
import pytest
from shapely.geometry import GeometryCollection, Point
from shapely.geometry import shape as shapely_shape

gaz = Pleiades()


class TestPleiades:
    def test_init(self):
        # Pleiades should have a web backend
        global gaz
        gaz.backend = "web"


class TestPleiadesWeb:
    """
    Test Pleiades functionality using the web backend.
    """

    def test_get_web(self):
        global gaz
        gaz.backend = "web"
        place = gaz.get("295374")
        assert place.raw["title"] == "Zucchabar"
        assert place.id == "295374"
        assert place.properties.title == "Zucchabar"
        assert set(place.names.name_strings) == {
            "Zouchabbari",
            "Zouchábbari",
            "Ζουχάββαρι",
            "Zucchabar",
        }
        names = place.names.get_names("Ζουχάββαρι")
        assert len(names) == 1
        n = names[0]
        assert n.toponym == "Ζουχάββαρι"
        assert n.language_tag == "grc"
        assert set(n.romanizations) == {"Zouchabbari", "Zouchábbari"}
        assert isinstance(place.geometry, geojson.GeometryCollection)
        assert len(place.geometry) == 2
        for geo in place.geometry.geometries:
            assert isinstance(geo, Point)

    def test_search_bounding_box(self):
        global gaz
        gaz.backend = "web"
        q = PleiadesQuery()
        bounds = (2.0, 36.0, 2.5, 36.5)
        q.set_parameter("bbox", bounds)
        results = gaz.search(q)
        assert len(results["hits"]) == 8
        ids = {hit["id"] for hit in results["hits"]}
        expected = {
            "295216",
            "295275",
            "295304",
            "295340",
            "295342",
            "295366",
            "295374",
            "296719",
        }
        assert ids == expected

    def test_search_description(self):
        global gaz
        gaz.backend = "web"
        q = PleiadesQuery()
        q.set_parameter("description", "Punic")
        results = gaz.search(q)
        assert len(results["hits"]) >= 74

    def test_search_description_or(self):
        global gaz
        gaz.backend = "web"
        q = PleiadesQuery()
        q.set_parameter("description", ["contested", "conflict"], "OR")
        results = gaz.search(q)
        assert len(results["hits"]) >= 10

    def test_search_description_and(self):
        global gaz
        gaz.backend = "web"
        q = PleiadesQuery()
        q.set_parameter("description", ["contested", "conflict"], "AND")
        results = gaz.search(q)
        assert len(results["hits"]) == 1

    def test_search_feature_type_or(self):
        global gaz
        gaz.backend = "web"
        q = PleiadesQuery()
        q.set_parameter("feature_type", ["acropolis", "agora"], "OR")
        results = gaz.search(q)
        assert len(results["hits"]) == 25

    def test_search_tag(self):
        global gaz
        gaz.backend = "web"
        q = PleiadesQuery()
        q.set_parameter("tag", "Ammon")
        results = gaz.search(q)
        assert len(results["hits"]) == 1

    def test_search_tag_or(self):
        global gaz
        gaz.backend = "web"
        q = PleiadesQuery()
        q.set_parameter("tag", ["Ammon", "Amun"], "OR")
        results = gaz.search(q)
        assert len(results["hits"]) == 2

    def test_search_tag_and(self):
        global gaz
        gaz.backend = "web"
        q = PleiadesQuery()
        q.set_parameter("tag", ["Magna Mater", "Mithras"], "AND")
        results = gaz.search(q)
        assert len(results["hits"]) == 1

    def test_search_title(self):
        global gaz
        gaz.backend = "web"
        q = PleiadesQuery()
        q.set_parameter("title", "Zucchabar")
        results = gaz.search(q)
        assert len(results["hits"]) == 1
        hit = results["hits"][0]
        assert hit["id"] == "295374"
        assert hit["title"] == "Zucchabar"
        assert hit["uri"] == "https://pleiades.stoa.org/places/295374"
        assert hit["summary"].startswith(
            "Zucchabar was an ancient city of Mauretania Caesariensis with Punic origins."
        )

    def test_search_text_simple(self):
        global gaz
        gaz.backend = "web"
        q = PleiadesQuery()
        q.set_parameter("text", "Miliana")
        results = gaz.search(q)
        assert len(results["hits"]) == 4
        for hit in results["hits"]:
            assert hit["id"] in ["315048", "295374", "295304", "315104"]

    def test_search_text_or(self):
        global gaz
        gaz.backend = "web"
        q = PleiadesQuery()
        q.set_parameter("text", ["Zucchabar", "Luxmanda"], "OR")
        results = gaz.search(q)
        assert len(results["hits"]) == 2
        for hit in results["hits"]:
            assert hit["id"] in ["295374", "896643025"]

    def test_search_text_and(self):
        global gaz
        gaz.backend = "web"
        q = PleiadesQuery()
        q.set_parameter("text", ["Zucchabar", "Miliana"], "AND")
        results = gaz.search(q)
        assert len(results["hits"]) == 1
        assert results["hits"][0]["id"] == "295374"

    def test_search_combo_1(self):
        global gaz
        gaz.backend = "web"
        q = PleiadesQuery()
        q.set_parameter("tag", ["Cybele", "Kybele", "Magna Mater"], "OR")
        q.set_parameter("feature_type", ["sanctuary", "temple-2"], "OR")
        results = gaz.search(q)
        assert len(results["hits"]) == 5
        expected = {"778145953", "550437", "87367170", "114722047", "109133"}
        ids = {hit["id"] for hit in results["hits"]}
        assert expected == ids

    def test_search_combo_2(self):
        global gaz
        gaz.backend = "web"
        q = PleiadesQuery()
        q.set_parameter("feature_type", ["sanctuary", "temple-2"], "OR")
        q.set_parameter("bbox", (27.5, 35.75, 28.3, 36.5))  # Rhodes and environs
        results = gaz.search(q)
        assert len(results["hits"]) == 4
        expected = {"589700", "590099", "630398334", "414067217"}
        ids = {hit["id"] for hit in results["hits"]}
        assert expected == ids


class TestPleiadesQueries:
    """
    Test defintion of queries for the Pleiades web interface
    """

    def test_query(self):
        q = PleiadesQuery()
        assert set(q.supported_parameters) == {
            "bbox",
            "description",
            "feature_type",
            "tag",
            "text",
            "title",
        }
        assert set(q.parameters_for_web.keys()) == {
            "portal_type:list",
            "review_state:list",
        }
        with pytest.raises(ValueError):
            q.set_parameter("foo", "bar")
        examples = {
            "bbox": (2.0, 36.0, 2.5, 36.5),
            "description": "Punic",
            "tag": "Ammon",
            "feature_type": "temple-2",
            "text": "unusual",
        }
        for name, value in examples.items():
            q.set_parameter(name, value)
        assert q.parameters == {
            "bbox": ((2.0, 36.0, 2.5, 36.5), None),
            "description": ("Punic", None),
            "tag": ("Ammon", None),
            "feature_type": ("temple-2", None),
            "text": ("unusual", None),
        }
        q.set_parameter("tag", [("Ammon", "Amun"), "OR"])
        assert q.parameters["tag"] == ([("Ammon", "Amun"), "OR"], None)
        assert q.parameters_for_web == {
            "Description": "Punic",
            "getFeatureType": "temple-2",
            "location_precision:list": "precise",
            "lowerLeft": "2.0001,36.0001",  # shaved bbox coordinates because of weird Pleiades geosearch behavior
            "portal_type:list": "Place",
            "predicate": "intersection",
            "review_state:list": "published",
            "SearchableText": "unusual",
            "Subject:list": [("Ammon", "Amun"), "OR"],
            "upperRight": "2.4999,36.4999",  # shaved
        }


class TestPleiadesSerialization:
    def test_json(self):
        global gaz
        gaz.backend = "web"
        place = gaz.get("295374")
        s = json.dumps(place, cls=ApographeEncoder, ensure_ascii=False)
        d = json.loads(s)
        assert set(d.keys()) == {
            "id_internal",
            "id",
            "uri",
            "properties",
            "names",
            "geometry",
        }
        assert isinstance(d["id_internal"], str)
        assert d["id"] == "295374"
        assert d["uri"] == "https://pleiades.stoa.org/places/295374"

        assert d["properties"]["title"] == "Zucchabar"
        # assert d["properties"]["ccodes"]  Pleiades doesn't do country codes

        assert len(d["names"]) == 2
        for name in d["names"]:
            try:
                toponym = name["toponym"]
            except KeyError:
                toponym = None
            else:
                if toponym is None:
                    assert set(name["romanizations"]) == {"Zucchabar"}
                elif toponym == "Ζουχάββαρι":
                    assert len(name) == 3
                    assert (
                        name["language_tag"] == "grc"
                    )  # pleiades assumes grc == grc-Grek even though IANA doesn't
                    assert set(name["romanizations"]) == {"Zouchábbari", "Zouchabbari"}
        assert isinstance(d["geometry"], dict)
        shape = shapely_shape(d["geometry"])
        assert isinstance(shape, GeometryCollection)
        geometries = d["geometry"]["geometries"]
        assert len(geometries) == 2
        for geometry in geometries:
            shape = shapely_shape(geometry)
            assert isinstance(shape, Point)

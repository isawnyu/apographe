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
from apographe.web import BackendWeb
import geojson
import logging
import pytest
from shapely.geometry import Point


class TestPleiades:
    p = Pleiades()

    def test_init(self):
        # Pleiades should have a web backend
        self.p.backend = "web"


class TestPleiadesWeb:
    """
    Test Pleiades functionality using the web backend.
    """

    p = Pleiades()

    def test_get_web(self):
        self.p.backend = "web"
        place = self.p.get("295374")
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
        q = PleiadesQuery()
        bounds = (2.0, 36.0, 2.5, 36.5)
        q.set_parameter("bbox", bounds)
        results = self.p.search(q)
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
        q = PleiadesQuery()
        q.set_parameter("description", "Punic")
        results = self.p.search(q)
        assert len(results["hits"]) >= 74

    def test_search_description_or(self):
        q = PleiadesQuery()
        q.set_parameter("description", ["contested", "conflict"], "OR")
        results = self.p.search(q)
        assert len(results["hits"]) >= 10

    def test_search_description_and(self):
        q = PleiadesQuery()
        q.set_parameter("description", ["contested", "conflict"], "AND")
        results = self.p.search(q)
        assert len(results["hits"]) == 1

    def test_search_feature_type_or(self):
        q = PleiadesQuery()
        q.set_parameter("feature_type", ["acropolis", "agora"], "OR")
        results = self.p.search(q)
        assert len(results["hits"]) == 25

    def test_search_tag(self):
        q = PleiadesQuery()
        q.set_parameter("tag", "Ammon")
        results = self.p.search(q)
        assert len(results["hits"]) == 1

    def test_search_tag_or(self):
        q = PleiadesQuery()
        q.set_parameter("tag", ["Ammon", "Amun"], "OR")
        results = self.p.search(q)
        assert len(results["hits"]) == 2

    def test_search_tag_and(self):
        q = PleiadesQuery()
        q.set_parameter("tag", ["Magna Mater", "Mithras"], "AND")
        results = self.p.search(q)
        assert len(results["hits"]) == 1

    def test_search_title(self):
        q = PleiadesQuery()
        q.set_parameter("title", "Zucchabar")
        results = self.p.search(q)
        assert len(results["hits"]) == 1
        hit = results["hits"][0]
        assert hit["id"] == "295374"
        assert hit["title"] == "Zucchabar"
        assert hit["uri"] == "https://pleiades.stoa.org/places/295374"
        assert hit["summary"].startswith(
            "Zucchabar was an ancient city of Mauretania Caesariensis with Punic origins."
        )

    def test_search_text_simple(self):
        q = PleiadesQuery()
        q.set_parameter("text", "Miliana")
        results = self.p.search(q)
        assert len(results["hits"]) == 4
        for hit in results["hits"]:
            assert hit["id"] in ["315048", "295374", "295304", "315104"]

    def test_search_text_or(self):
        q = PleiadesQuery()
        q.set_parameter("text", ["Zucchabar", "Luxmanda"], "OR")
        results = self.p.search(q)
        assert len(results["hits"]) == 2
        for hit in results["hits"]:
            assert hit["id"] in ["295374", "896643025"]

    def test_search_text_and(self):
        q = PleiadesQuery()
        q.set_parameter("text", ["Zucchabar", "Miliana"], "AND")
        results = self.p.search(q)
        assert len(results["hits"]) == 1
        assert results["hits"][0]["id"] == "295374"

    def test_search_combo_1(self):
        q = PleiadesQuery()
        q.set_parameter("tag", ["Cybele", "Kybele", "Magna Mater"], "OR")
        q.set_parameter("feature_type", ["sanctuary", "temple-2"], "OR")
        results = self.p.search(q)
        assert len(results["hits"]) == 5
        expected = {"778145953", "550437", "87367170", "114722047", "109133"}
        ids = {hit["id"] for hit in results["hits"]}
        assert expected == ids

    def test_search_combo_2(self):
        q = PleiadesQuery()
        q.set_parameter("feature_type", ["sanctuary", "temple-2"], "OR")
        q.set_parameter("bbox", (27.5, 35.75, 28.3, 36.5))  # Rhodes and environs
        results = self.p.search(q)
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

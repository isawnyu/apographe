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
import pytest


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

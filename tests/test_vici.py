#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Test the apographe.vici module
"""

from apographe.vici import Vici, ViciQuery
from apographe.serialization import ApographeEncoder
from apographe.web import BackendWeb
import geojson
import json
import logging
from pprint import pformat
import pytest
from shapely.geometry import GeometryCollection, Point
from shapely.geometry import shape as shapely_shape

gaz = Vici()


class TestVici:
    def test_init(self):
        # Vici should have a web backend
        global gaz
        gaz.backend = "web"


class TestViciWeb:
    """
    Test Vici functionality using the web backend.
    """

    def test_search_bounding_box(self):
        global gaz
        gaz.backend = "web"
        q = ViciQuery()
        bounds = (2.0, 36.0, 2.5, 36.5)
        q.set_parameter("bbox", bounds)
        results = gaz.search(q)
        assert len(results["hits"]) == 5
        ids = {hit["id"] for hit in results["hits"]}
        expected = {
            "3956",
            "3958",
            "19818",
            "22829",
            "22830",
        }
        assert ids == expected

    def test_search_text_simple(self):
        global gaz
        gaz.backend = "web"
        q = ViciQuery()
        q.set_parameter("text", "Zucchabar")
        results = gaz.search(q)
        assert len(results["hits"]) == 1
        for hit in results["hits"]:
            assert hit["id"] == "22829"

#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Test the apographe.edh module
"""

from apographe.edh import EDH, EDHQuery
from apographe.serialization import ApographeEncoder
from apographe.web import BackendWeb
import json
import logging
import pytest
from shapely.geometry import GeometryCollection, Point
from shapely.geometry import shape as shapely_shape

gaz = EDH()


class TestEDH:
    def test_init(self):
        # EDH should have a web backend
        global gaz
        gaz.backend = "web"


class TestEDHWeb:
    """
    Test Pleiades functionality using the web backend.
    """

    def test_get_web(self):
        global gaz
        gaz.backend = "web"
        place = gaz.get("G013662")
        assert place.id == "G013662"
        assert place.properties.title == "Zucchabar - Miliana"
        assert set(place.names.name_strings) == {"Miliana", "Zucchabar"}
        names = place.names.get_names("Miliana")
        assert len(names) == 1
        n = names[0]
        assert n.language_tag == "und"
        assert set(n.romanizations) == {"Miliana"}
        names = place.names.get_names("Zucchabar")
        assert len(names) == 1
        n = names[0]
        assert n.language_tag == "und"
        assert set(n.romanizations) == {"Zucchabar"}
        import logging

        logger = logging.getLogger(self.__class__.__name__)
        logger.debug(type(place.geometry))
        assert isinstance(place.geometry, Point)

    def test_search_title(self):
        global gaz
        gaz.backend = "web"
        q = EDHQuery()
        q.set_parameter("title", "Zucchabar")
        results = gaz.search(q)
        assert len(results["hits"]) == 1
        hit = results["hits"][0]
        assert hit["id"] == "G013662"
        assert hit["title"] == "Zucchabar - Miliana"
        assert hit["uri"] == "https://edh.ub.uni-heidelberg.de/edh/geographie/G013662"
        assert hit["summary"].startswith("Ech Cheliff, Algeria")
        q.set_parameter("title", "Miliana")
        results = gaz.search(q)
        assert len(results["hits"]) == 2
        ids = [h["id"] for h in results["hits"]]
        assert set(ids) == {"G013662", "G013608"}

    def test_search_description(self):
        global gaz
        gaz.backend = "web"
        q = EDHQuery()
        q.set_parameter("description", "Ech Cheliff")
        results = gaz.search(q)
        assert len(results["hits"]) == 5

    def test_search_text(self):
        global gaz
        gaz.backend = "web"
        q = EDHQuery()
        q.set_parameter("text", "garden")
        results = gaz.search(q)
        assert len(results["hits"]) == 26

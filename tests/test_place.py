#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Test the apographe.place module
"""

from apographe.linked_places_format import dumps as lpfdumps
from apographe.place import Place
from apographe.serialization import ApographeEncoder
import json
import logging
from pprint import pformat
from shapely.geometry import Point
from shapely.geometry import shape as shapely_shape


class TestPlace:
    def test_save(self):
        kwargs = {
            "raw": None,
            "id": "zucchabar",
            "title": "Zucchabar",
            "ccodes": ["Algeria"],
            "names": [
                {
                    "toponym": "Ζουχάββαρι",
                    "romanizations": ["Zouchábbari", "Zouchabbari"],
                    "language_tag": "grc-Grek",
                }
            ],
            "geometry": {
                "type": "Point",
                "coordinates": [2.2237580000000001, 36.304938999999997],
            },
        }
        p = Place(**kwargs)
        assert p.properties.title == "Zucchabar"
        assert p.properties.ccodes == ["DZ"]
        assert p.properties.country_names == ["Algeria"]
        assert len(p.names) == 1
        assert set(p.names.name_strings) == {"Zouchabbari", "Zouchábbari", "Ζουχάββαρι"}
        names = p.names.get_names("Z")
        assert len(names) == 1
        n = names[0]
        assert n.toponym == "Ζουχάββαρι"
        assert set(n.romanizations) == {"Zouchabbari", "Zouchábbari"}
        assert n.language_tag == "grc-Grek"
        assert n.language_subtag == "grc"
        assert n.script_subtag == "Grek"
        assert n.region_subtag is None
        assert isinstance(p.geometry, Point)

        jstring = json.dumps(p, cls=ApographeEncoder, indent=4, ensure_ascii=False)
        d = json.loads(jstring)
        assert set(d.keys()) == {
            "id_internal",
            "id",
            "properties",
            "names",
            "geometry",
        }
        assert isinstance(d["id_internal"], str)
        assert d["id"] == "zucchabar"

        assert d["properties"]["title"] == "Zucchabar"
        assert d["properties"]["ccodes"] == ["DZ"]

        assert len(d["names"]) == 1
        name = d["names"][0]
        assert len(name) == 3
        assert name["language_tag"] == "grc-Grek"
        assert name["toponym"] == "Ζουχάββαρι"
        assert set(name["romanizations"]) == {"Zouchábbari", "Zouchabbari"}

        assert isinstance(d["geometry"], dict)
        shape = shapely_shape(d["geometry"])
        assert isinstance(shape, Point)
        assert [shape.x, shape.y] == [2.2237580000000001, 36.304938999999997]

        s = lpfdumps(p)
        d = json.loads(s)  # sic
        assert set(d.keys()) == {
            "type",
            "@context",
            "features",
        }
        features = d["features"]
        assert len(features) == 1
        f = features[0]
        assert set(f.keys()) == {
            "id_internal",
            "id",
            "properties",
            "names",
            "geometry",
        }
        assert isinstance(f["id_internal"], str)
        assert f["id"] == "zucchabar"

        assert f["properties"]["title"] == "Zucchabar"
        assert f["properties"]["ccodes"] == ["DZ"]

        assert len(f["names"]) == 1
        name = f["names"][0]
        assert len(name) == 3
        assert name["language_tag"] == "grc-Grek"
        assert name["toponym"] == "Ζουχάββαρι"
        assert set(name["romanizations"]) == {"Zouchábbari", "Zouchabbari"}

        assert isinstance(f["geometry"], dict)
        shape = shapely_shape(f["geometry"])
        assert isinstance(shape, Point)
        assert [shape.x, shape.y] == [2.2237580000000001, 36.304938999999997]

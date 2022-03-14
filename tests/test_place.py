#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Test the apographe.place module
"""

from apographe.place import Place
from shapely.geometry import Point


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
        assert isinstance(p.geometry, list)
        

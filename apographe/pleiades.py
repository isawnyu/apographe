#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Gazetteer Inferface for the Pleiades gazetteer of ancient places
"""

from apographe.gazetteer import Gazetteer
from apographe.query import Query
from apographe.web import BackendWeb
import logging

logger = logging.getLogger(__name__)


class Pleiades(BackendWeb, Gazetteer):
    def __init__(self):
        Gazetteer.__init__(self, name="Pleiades")
        kwargs = {
            "place_netloc": "pleiades.stoa.org",
            "place_scheme": "https",
            "place_path": "/places/",
            "place_suffix": "/json",
            "user_agent": "ApographeTester/0.0.1 (+https://github.org/isawnyu/apographe)",
        }
        BackendWeb.__init__(self, **kwargs)


class PleiadesQuery(Query):
    def __init__(self):
        Query.__init__(self)
        self._supported_parameters = {
            "bbox": {"expected": (tuple), "behavior": self._preprocess_bbox},
            "description": {
                "expected": (str, list),
                "list_behavior": "join",
                "rename": "Description",
            },
            "feature_type": {
                "expected": (str, list),
                "list_behavior": "noseq",
                "list_additional": {"AND": {"get_usage:ignore_empty": "operator:and"}},
                "rename": "getFeatureType",
            },
            "tag": {
                "expected": (str, list),
                "list_behavior": "noseq",
                "list_additional": {
                    "AND": {"Subject_usage:ignore_empty": "operator:and"}
                },
                "rename": "Subject:list",
            },
            "text": {
                "expected": (str, list),
                "list_behavior": "join",
                "rename": "SearchableText",
            },
            "title": {"expected": str, "rename": "Title"},
        }
        self._default_web_parameters = {
            "portal_type:list": "Place",
            "review_state:list": "published",
        }

    def _preprocess_bbox(self, bounds: tuple):
        shaved_bounds = list()  # pleiades is weird
        for i in [0, 1]:
            shaved_bounds.append(bounds[i] + 0.0001)
        for i in [2, 3]:
            shaved_bounds.append(bounds[i] - 0.0001)
        return {
            "lowerLeft": f"{shaved_bounds[0]},{shaved_bounds[1]}",
            "upperRight": f"{shaved_bounds[2]},{shaved_bounds[3]}",
            "predicate": "intersection",
            "location_precision:list": "precise",
        }

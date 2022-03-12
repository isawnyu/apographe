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
from apographe.place import Place
from apographe.query import Query
from apographe.web import BackendWeb
import feedparser
import logging
from pprint import pformat
from urllib.parse import urlunparse


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
        """Shave a small amount off the bounding box to keep Pleiades from expanding the search area."""
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


class Pleiades(BackendWeb, Gazetteer):
    def __init__(self):
        Gazetteer.__init__(self, name="Pleiades")
        kwargs = {
            "place_netloc": "pleiades.stoa.org",
            "place_scheme": "https",
            "place_path": "/places/",
            "place_suffix": "/json",
            "search_netloc": "pleiades.stoa.org",
            "search_scheme": "https",
            "search_path": "/search_rss",
            "user_agent": "ApographeTester/0.0.1 (+https://github.org/isawnyu/apographe)",
        }
        BackendWeb.__init__(self, **kwargs)

    def get(self, id: str):
        backend = self.backend
        place = getattr(self, f"_pleiades_{backend}_get")(id)
        return place

    def search(self, query: PleiadesQuery):
        if not isinstance(query, PleiadesQuery):
            raise TypeError(
                f"Expected query of type {PleiadesQuery} but got {type(query)}."
            )
        backend = self.backend
        return getattr(self, f"_pleiades_{backend}_search")(query)

    def _pleiades_web_get(self, id: str):
        data = BackendWeb.get(self, id).json()
        kwargs = self._kwargs_from_json(data)
        place = Place(id=id, raw=data, **kwargs)
        return place

    def _kwargs_from_json(self, data):
        kwargs = dict()
        copy_keys = ["title"]
        for k in copy_keys:
            kwargs[k] = data[k]
        kwargs["names"] = [self._kwargs_from_json_name(n) for n in data["names"]]
        return kwargs

    def _kwargs_from_json_name(self, name):
        name_kwargs = dict()
        crosswalk = {
            "attested": ("toponym", "copy"),
            "romanized": ("romanizations", "split-comma"),
            "language": ("language_tag", "copy"),
        }
        for src, rule in crosswalk.items():
            if name[src]:
                dest, action = rule
                if action == "copy":
                    name_kwargs[dest] = name[src]
                elif action == "split-comma":
                    name_kwargs[dest] = name[src].split(",")
        return name_kwargs

    def _pleiades_web_search(self, query: PleiadesQuery):
        params = self._prep_params(**query.parameters_for_web)
        config = self.backend_configuration("web")
        query_uri = urlunparse(
            (
                config["search_scheme"],
                config["search_netloc"],
                config["search_path"],
                "",
                params,
                "",
            )
        )
        r = BackendWeb.search(self, query_uri)
        hits = list()
        data = feedparser.parse(r.text)
        for entry in data.entries:
            hits.append(
                {
                    "id": entry.link.split("/")[-1],
                    "uri": entry.link,
                    "title": entry.title,
                    "summary": entry.description,
                }
            )
        return {"query": query_uri, "hits": hits}

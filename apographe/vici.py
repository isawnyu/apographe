#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Gazetteer Inferface for the vici.org archaeological atlas of antiquity
"""

from apographe.gazetteer import Gazetteer
from apographe.place import Place
from apographe.query import Query
from apographe.web import BackendWeb
from copy import deepcopy
import feedparser
import logging
from pprint import pformat
from datetime import timedelta
from urllib.parse import urlunparse


class ViciQuery(Query):
    def __init__(self):
        Query.__init__(self)
        self._supported_parameters = {
            "bbox": {"expected": (tuple, str), "behavior": self._preprocess_bbox},
        }
        self._default_web_parameters = {"zoom": "11"}

    def _preprocess_bbox(self, bounds):
        """Prepare bbox parameters."""
        if isinstance(bounds, str):
            these_bounds = [float(s) for s in bounds.split(",")]
        elif isinstance(bounds, (list, tuple)):
            these_bounds = bounds
        # vici does comma-delimited string of latitude, longitude of south-west point, latitude, longitude of north-east point.
        return {
            "bounds": f"{these_bounds[1]},{these_bounds[0]},{these_bounds[3]},{these_bounds[2]}",
        }


class Vici(BackendWeb, Gazetteer):
    """Interface for the vici.org archaeological atlas of antiquity."""

    def __init__(self):
        Gazetteer.__init__(self, name="Vici")
        # NB: vici.org sets the following response headers:
        # Expires: Thu, 19 Nov 1981 08:52:00 GMT
        # Cache-Control: no-store, no-cache, must-revalidate
        # These settings will result in no caching if webiquette is
        # invoked with cache_control=True, so we will disable that
        # functionality and set a local TTL of 6 hours
        kwargs = {
            "place_netloc": "vici.org",
            "place_scheme": "https",
            "place_path": "/vici/",
            "place_suffix": "/json",
            "search_netloc": "vici.org",
            "search_scheme": "https",
            "search_path": "/geojson.php",
            "expire_after": timedelta(hours=6),
            "respect_robots_txt": False,
        }
        BackendWeb.__init__(self, **kwargs)

    def get(self, id: str):
        backend = self.backend
        place = getattr(self, f"_vici_{backend}_get")(id)
        return place

    def search(self, query: ViciQuery):
        if not isinstance(query, ViciQuery):
            raise TypeError(
                f"Expected query of type {ViciQuery} but got {type(query)}."
            )
        backend = self.backend
        return getattr(self, f"_vici_{backend}_search")(query)

    def _vici_web_get(self, id: str):
        data = BackendWeb.get(self, id).json()
        kwargs = self._kwargs_from_json(data)
        place = Place(id=id, raw=data, **kwargs)
        return place

    def _kwargs_from_json(self, data):
        kwargs = dict()
        copy_keys = ["title", "uri"]

        # names
        for k in copy_keys:
            kwargs[k] = data[k]
        try:
            kwargs["names"] = [self._kwargs_from_json_name(n) for n in data["names"]]
        except KeyError:
            kwargs["names"] = []

        # descriptions
        kwargs["descriptions"] = []
        try:
            data["description"]
        except KeyError:
            pass
        else:
            kwargs["descriptions"].append(
                {
                    "value": data["description"],
                    "language_tag": "en",
                    "id": f"{data['uri']}#description",
                }
            )
        try:
            data["details"]
        except KeyError:
            pass
        else:
            kwargs["descriptions"].append(
                {
                    "value": data["details"],
                    "language_tag": "en",
                    "id": f"{data['uri']}#description",
                },
            )

        # geometries
        try:
            kwargs["geometries"] = [
                self._kwargs_from_json_geometry(l["geometry"])
                for l in data["locations"]
            ]
        except KeyError:
            kwargs["geometries"] = []
        return kwargs

    def _kwargs_from_json_geometry(self, geometry):
        return deepcopy(geometry)

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
                else:
                    raise NotImplementedError(action)
        return name_kwargs

    def _vici_web_search(self, query: ViciQuery):
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
        j = r.json()
        logger = logging.getLogger()
        logger.debug(pformat(j, indent=4))
        for entry in j["features"]:
            hits.append(
                {
                    "id": str(entry["id"]),
                    "uri": f"https://vici.org/{entry['properties']['url']}",
                    "title": entry["properties"]["title"],
                    "summary": entry["properties"]["summary"],
                }
            )
        return {"query": query_uri, "hits": hits}

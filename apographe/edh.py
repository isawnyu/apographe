#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Epigraphic Database Heidelberg Geography interface
"""

from apographe.gazetteer import Gazetteer
from apographe.place import Place
from apographe.query import Query
from apographe.text import normtext
from apographe.web import BackendWeb
from urllib.parse import urlunparse


class EDHQuery(Query):
    def __init__(self):
        Query.__init__(self)
        self._supported_parameters = {
            # EDH search does not support:
            # "bbox": {"expected": (tuple), "behavior": self._preprocess_bbox},
            # "feature_type": {
            #     "expected": (str, list),
            #     "list_behavior": "noseq",
            #     "list_additional": {"AND": {"get_usage:ignore_empty": "operator:and"}},
            #     "rename": "getFeatureType",
            # },
            # "tag": {
            #     "expected": (str, list),
            #     "list_behavior": "noseq",
            #     "list_additional": {
            #         "AND": {"Subject_usage:ignore_empty": "operator:and"}
            #     },
            #     "rename": "Subject:list",
            # },
            "description": {
                "expected": (str, list),
                "list_behavior": "join",
                "rename": "commentary",
            },
            "text": {
                "expected": (str, list),
                "behavior": self._preprocess_text,
            },
            "title": {"expected": str, "behavior": self._preprocess_title},
        }
        self._default_web_parameters = {"limit": "100"}


class EDH(BackendWeb, Gazetteer):
    def __init__(self):
        Gazetteer.__init__(self, name="Pleiades")
        kwargs = {
            "place_netloc": "edh.ub.uni-heidelberg.de",
            "place_scheme": "https",
            "place_path": "/edh/geographie/",
            "place_suffix": "/json",
            "search_netloc": "edh.ub.uni-heidelberg.de",
            "search_scheme": "https",
            "search_path": "/data/api/geographie/suche",
        }
        BackendWeb.__init__(self, **kwargs)

    def get(self, id: str):
        backend = self.backend
        place = getattr(self, f"_edh_{backend}_get")(id)
        return place

    def search(self, query: EDHQuery):
        if not isinstance(query, EDHQuery):
            raise TypeError(f"Expected query of type {EDHQuery} but got {type(query)}.")
        backend = self.backend
        return getattr(self, f"_edh_{backend}_search")(query)

    def _edh_web_get(self, id: str):
        data = BackendWeb.get(self, id).json()
        from pprint import pformat
        import logging

        logger = logging.getLogger(self.__class__.__name__)
        logger.debug(pformat(data, indent=4))
        datum = data["items"]
        kwargs = self._kwargs_from_json(datum)
        place = Place(id=id, raw=datum, **kwargs)
        return place

    def _edh_web_search(self, query: EDHQuery):
        pass

    def _kwargs_from_json(self, data):
        kwargs = dict()
        copy_keys = []
        for k in copy_keys:
            kwargs[k] = data[k]
        kwargs["title"] = self._kwargs_title(data)
        kwargs["uri"] = f"https://edh.ub.uni-heidelberg.de/edh/geographie/{data['id']}"
        kwargs["names"] = []
        for k in ["findspot", "findspot_modern"]:
            try:
                v = data[k]
            except KeyError:
                pass
            else:
                if v:
                    nv = normtext(v)
                    name = {"language_tag": "und", "romanizations": set()}
                    name["attested"] = nv
                    name["romanizations"].add(nv)
                    if k == "findspot_modern":
                        name["language_code"] = "de"
                    # name["name_type"] = "geographic"
                    kwargs["names"].append(name)
        try:
            v = data["findspot_ancient"]
        except KeyError:
            pass
        else:
            if v:
                nv = normtext(v)
                name = {"language_code": "und", "romanizations": set()}
                name["romanizations"].add(nv)
                # name["name_type"] = "geographic"
                kwargs["names"].append(name)
        keys = [k for k in data.keys() if k.startswith("coordinates")]
        kwargs["geometries"] = list()
        for k in keys:
            coords = data[k]
            lat, lon = [float(normtext(c)) for c in coords.split(",")]
            g = {"type": "Point", "coordinates": (lon, lat)}
            kwargs["geometries"].append(g)

        return kwargs

    def _kwargs_title(self, data):
        for k in ["findspot", "findspot_modern", "findspot_ancient"]:
            try:
                data[k]
            except KeyError:
                data[k] = None
        if data["findspot_ancient"] and data["findspot_modern"] and data["findspot"]:
            title = f"{data['findspot_ancient']} - {data['findspot_modern']} ({data['findspot']})"
        elif data["findspot_ancient"] and data["findspot_modern"]:
            title = f"{data['findspot_ancient']} - {data['findspot_modern']}"
        elif data["findspot_ancient"] and data["findspot"]:
            title = f"{data['findspot_ancient']} ({data['findspot']})"
        elif data["findspot_modern"] and data["findspot"]:
            title = f"{data['findspot_modern']} ({data['findspot']})"
        elif data["findspot_ancient"]:
            title = f"{data['findspot_ancient']}"
        elif data["findspot_modern"]:
            title = f"{data['findspot_modern']}"
        elif data["findspot"]:
            title = f"{data['findspot']}"
        else:
            title = None
        return title

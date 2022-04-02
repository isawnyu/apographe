#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Gazetteer Inferface for the German Archaeological Institute gazetteer (idai)
"""

from apographe.gazetteer import Gazetteer
from apographe.languages_and_scripts import check_script, romanize
from apographe.place import Place
from apographe.query import Query
from apographe.web import BackendWeb
from copy import deepcopy
from geojson import Point
from iso639 import Lang as Lang639
from language_tags import tags
import logging
from pprint import pformat
from urllib.parse import urlunparse


class IDAIQuery(Query):
    def __init__(self):
        Query.__init__(self)
        self._supported_parameters = {
            "text": {
                "expected": (str, list),
                "list_behavior": "join",
                "rename": "q",
            },
        }
        self._default_web_parameters = {}


class IDAI(BackendWeb, Gazetteer):
    """Interface for the iDAI Gazetteer of the German Archaeological Institute."""

    def __init__(self):
        Gazetteer.__init__(self, name="iDAI")
        # NB: iDAI sets the following response headers
        # Cache-Control: no-cache, no-store, max-age=0, must-revalidate
        # Expires: 0
        # but we want better performance on repeated calls in a session, so
        # we tell requests-cache (through webiquette) to:
        # 1. ignore the Cache-Control response header (cache_control = False)
        # 2. set a per-session expiration time of 6 hours in seconds (expire_after = 21600)
        kwargs = {
            "place_netloc": "gazetteer.dainst.org",
            "place_scheme": "https",
            "place_path": "/doc/",
            "place_suffix": ".json",
            "search_netloc": "gazetteer.dainst.org",
            "search_scheme": "https",
            "search_path": "search.json",
            "cache_control": False,
            "expire_after": 21600,
        }
        BackendWeb.__init__(self, **kwargs)

    def get(self, id: str):
        backend = self.backend
        place = getattr(self, f"_idai_{backend}_get")(id)
        return place

    def search(self, query: IDAIQuery):
        if not isinstance(query, IDAIQuery):
            raise TypeError(
                f"Expected query of type {IDAIQuery} but got {type(query)}."
            )
        backend = self.backend
        return getattr(self, f"_idai_{backend}_search")(query)

    def _dedupe_names(self, names: list):
        # we can get repeats from dai between prefName and other names
        d = dict()
        logger = logging.getLogger(self.__class__.__name__ + "._dedupe_names()")

        for n in names:
            try:
                toponym = n["toponym"]
            except KeyError:
                toponym = None
            if toponym:
                logger.debug(pformat(n, indent=4))
                hash = f"{n['language_tag']}:{toponym.lower().replace(' ', '')}"
            else:
                rom = sorted(
                    list(set([r.lower().replace(" ", "") for r in n["romanizations"]]))
                )
                hash = f"{n['language_tag']}:{rom[0]}"
            try:
                hit = d[hash]
            except KeyError:
                d[hash] = n
            else:
                if (
                    hit["toponym"] == n["toponym"]
                    and hit["language_tag"] == n["language_tag"]
                    and hit["romanizations"] == n["romanizations"]
                ):
                    pass
                else:
                    logger.error(pformat(hit, indent=4))
                    logger.error(pformat(n, indent=4))
                    raise RuntimeError()
        return list(d.values())

    def _idai_web_get(self, id: str):
        data = BackendWeb.get(self, id).json()
        kwargs = self._kwargs_from_json(data)
        place = Place(id=id, raw=data, **kwargs)
        logger = logging.getLogger(self.__class__.__name__ + "._ida_web_get()")
        logger.debug(pformat(place.asdict(), indent=4))
        return place

    def _kwargs_from_json(self, data):
        logger = logging.getLogger(self.__class__.__name__ + "._kwargs_from_json()")
        logger.debug(pformat(data, indent=4))
        kwargs = dict()
        kwargs["title"] = data["prefName"]["title"]
        kwargs["uri"] = data["@id"]
        names = [self._kwargs_from_json_name(data["prefName"])]
        names.extend([self._kwargs_from_json_name(n) for n in data["names"]])
        kwargs["names"] = self._dedupe_names(names)
        kwargs["geometries"] = [self._kwargs_from_json_geometry(data["prefLocation"])]

        desc = ""
        ancient_names = "/".join(
            sorted(
                [
                    n["title"]
                    for n in [na for na in data["names"] if "ancient" in na.keys()]
                    if n["ancient"]
                ]
            )
        )
        if ancient_names and ancient_names != data["prefName"]["title"]:
            desc = "Ancient name"
            if "/" in ancient_names:
                desc += "s"
            desc += f": {ancient_names}"
        if desc:
            desc += " ("
        place_types = "; ".join(sorted([pt.replace("-", " ") for pt in data["types"]]))
        desc += place_types
        if "(" in desc:
            desc += ")"
        kwargs["descriptions"] = [
            {"value": desc, "lang_code": "en", "id": f"{data['@id']}"}
        ]
        return kwargs

    def _kwargs_from_json_geometry(self, geometry):
        try:
            coords = geometry["coordinates"]
        except KeyError:
            raise NotImplementedError(pformat(geometry, indent=4))
        return Point(coords)

    def _kwargs_from_json_name(self, name):
        name_kwargs = dict()

        # {'ancient': True, 'title': 'Zucchabar'}
        # {'language': 'deu', 'title': 'Miliana'}

        try:
            ancient = name["ancient"]
        except KeyError:
            ancient = False
        try:
            language = name["language"]
        except KeyError:
            language_tag = None
        else:
            language_tag = tags.language(Lang639(language).pt1).format
        val = name["title"]
        if language_tag:
            name_kwargs["language_tag"] = language_tag
            name_kwargs["romanizations"] = romanize(val, language_tag)
            try:
                default_script = tags.language(language_tag).script.format
            except AttributeError:
                this_script = check_script(val)
                if language_tag == "sr" and this_script == "Cyrl":
                    name_kwargs["toponym"] = val
                elif language_tag == "zh" and this_script == "Hani":
                    name_kwargs["toponym"] = val
                else:
                    logger = logging.getLogger(
                        self.__class__.__name__ + "._kwargs_from_json_name()"
                    )
                    logger.error(
                        f"language tag '{language_tag}' has no default script."
                    )
            else:
                if check_script(val) == default_script:
                    name_kwargs["toponym"] = val
        else:
            name_kwargs["language_tag"] = "und"
            name_kwargs["romanizations"] = romanize(val)
        return name_kwargs

    def _idai_web_search(self, query: IDAIQuery):
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
        data = r.json()
        logger = logging.getLogger(self.__class__.__name__ + "._idai_web_search")
        logger.debug(pformat(data, indent=4))
        for entry in data["result"]:
            hits.append(
                {
                    "id": entry["@id"].split("/")[-1],
                    "uri": entry["@id"],
                    "title": entry["prefName"]["title"],
                    "summary": ", ".join([t.replace("-", " ") for t in entry["types"]]),
                }
            )
        return {"query": query_uri, "hits": hits}

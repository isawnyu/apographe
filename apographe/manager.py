#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Manage higher-level operations for an API
"""
from apographe.gazetteer import Gazetteer
from apographe.idai import IDAI, IDAIQuery
from apographe.pleiades import Pleiades, PleiadesQuery
from copy import deepcopy
from inspect import getdoc
import logging
from slugify import slugify


class Manager:
    """API"""

    def __init__(self):
        self.apographe = dict()  # local list of places
        self._gazetteers = {
            "idai": (IDAI, IDAIQuery),
            "pleiades": (Pleiades, PleiadesQuery),
        }
        self._search_results = dict()  # keep track of all search results this session
        self.logger = logging.getLogger(self.__class__.__name__)

    def accession(self, gazetteer_name: str, place_id: str):
        """Collect a place from a gazetteer and convert/copy it to the local list of places"""
        gazetteer_interface, gazetteer_query_class = self.get_gazetteer(gazetteer_name)
        gplace = gazetteer_interface.get(place_id)
        place_key = f"{gazetteer_name}:{place_id}"
        self.apographe[place_key] = gplace
        hit = {
            "place_key": place_key,
            "title": gplace.properties.title,
            "uri": gplace.uri,
            "summary": "NotImplemented",
        }
        return hit

    def get_gazetteer(self, gazetteer_name):
        """Get gazetteer interface and query class using the gazetteer name."""
        try:
            gazetteer_interface, gazetteer_query_class = self._invoke_gazetteer(
                gazetteer_name
            )
        except ValueError as err:
            if str(err) == gazetteer_name:
                gazetteers = " ".join(list(self._gazetteers.keys()))
                msg = (
                    f"Could not invoke gazetteer named '{gazetteer_name}'. "
                    f"Expected one of: {gazetteers.sort()}"
                )
                raise ValueError(self, msg)
            else:
                raise
        return (gazetteer_interface, gazetteer_query_class)

    def get_place(self, place_key):
        """Get a place from the internal gazetteer."""
        try:
            place = self.apographe[place_key]
        except ValueError:
            raise ValueError(place_key)
        return place

    def search(self, gazetteer_name, *args, **kwargs):
        """Search the indicated gazetteer."""
        gazetteer_interface, gazetteer_query_class = self.get_gazetteer(gazetteer_name)
        query = gazetteer_query_class()
        if len(args) > 1:
            query.set_parameter("text", list(args[1:]))
        for name, value in kwargs.items():
            query.set_parameter(name, value)
        results = gazetteer_interface.search(query)
        if results["hits"]:
            try:
                self._search_results[gazetteer_name]
            except KeyError:
                self._search_results[gazetteer_name] = dict()
            for hit in results["hits"]:
                self._search_results[gazetteer_name][hit["id"]] = hit
        return results["hits"]

    @property
    def search_results(self):
        """Get a list of all search hits so far this session.
        List is sorted by gazetteer name and title."""
        results = dict()  # keys will be dictionary names
        for gazetteer_name, hits in self._search_results.items():
            try:
                results[gazetteer_name]
            except KeyError:
                results[
                    gazetteer_name
                ] = dict()  # keys will be slugs made from hit titles
            for hit in hits.values():
                results[gazetteer_name][slugify(hit["title"])] = hit
        gazetteer_names = sorted(list(results.keys()))
        hits = list()
        for gazetteer_name in gazetteer_names:
            slugs = sorted([slug for slug in list(results[gazetteer_name].keys())])
            for slug in slugs:
                hit = deepcopy(results[gazetteer_name][slug])
                hit["gazetteer_name"] = gazetteer_name
                hits.append(hit)
        return hits

    @property
    def supported_gazetteers(self):
        """
        Get information about supported gazetteers.
        Returns a list of tuples containing a short name and a description for
        each gazetteer, like ("foo", "Foo is an epic gazetteer")
        """
        gazetteer_names = sorted(list(self._gazetteers.keys()))
        gazetteer_info = list()
        for gn in gazetteer_names:
            desc = getdoc(self._gazetteers[gn][0])
            desc = desc.replace("Interface for the ", "")
            if desc[-1] == ".":
                desc = desc[:-1]
            gazetteer_info.append((gn, desc))
        return gazetteer_info

    def _invoke_gazetteer(self, gazetteer_name: str):
        """Retrieve appropriate gazetteer interface (initialize if necessary)"""
        try:
            gaz_info = self._gazetteers[gazetteer_name]
        except KeyError:
            raise ValueError(gazetteer_name)
        if not isinstance(gaz_info[0], Gazetteer):
            gaz = gaz_info[0]()
            gaz.backend = "web"
            self._gazetteers[gazetteer_name] = (gaz, gaz_info[1])
            gaz_info = self._gazetteers[gazetteer_name]
        return gaz_info

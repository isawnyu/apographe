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
from apographe.linked_places_format import dump, load
from apographe.place import Place
from apographe.pleiades import Pleiades, PleiadesQuery
from copy import deepcopy
from inspect import getdoc
import logging
from pathlib import Path, PurePath
from pprint import pformat
from slugify import slugify
from sys import platform


class Manager:
    """API"""

    def __init__(self):
        self.apographe = dict()  # local list of places
        self._gazetteers = {
            "idai": (IDAI, IDAIQuery),
            "pleiades": (Pleiades, PleiadesQuery),
        }
        self.imports = dict()  # imported data
        self._search_results = dict()  # keep track of all search results this session
        self.logger = logging.getLogger(self.__class__.__name__)

    def accession(self, *args, **kwargs):
        # def accession(self, gazetteer_name: str, place_id: str):
        pids = list()
        if len(args) == 2 and len(kwargs) == 0:
            # Collect a place from a gazetteer and convert/copy it to the local list of places"""
            gazetteer_name, place_id = args
            pids = [place_id]
        elif len(args) == 1 and len(kwargs) == 1:
            # accession from imported list
            gazetteer_name = args[0]
            import_key = kwargs["imports"]
            pids = self.imports[import_key]
        else:
            raise ValueError("accession")
        gazetteer_interface, gazetteer_query_class = self.get_gazetteer(gazetteer_name)
        places = [gazetteer_interface.get(pid) for pid in pids]
        places = {slugify(p.properties.title): p for p in places}
        hits = list()
        for pid, place in places.items():
            try:
                self.apographe[pid]
            except KeyError:
                place.id = pid
                self.apographe[place.id] = place
            else:
                i = len([k for k in self.apographe.keys() if k.startswith(pid)])
                place_id = f"{pid}-{i}"
                place.id = place_id
                self.apographe[place.id] = place
            hit = {
                "id": pid,
                "title": place.properties.title,
                "uri": place.uri,
                "summary": place.descriptions.description_strings[0],
            }
            hits.append(hit)
        return hits

    def change(self, place_id: str, **kwargs):
        self.logger.debug(f"id: {id}")
        self.logger.debug(pformat(kwargs, indent=4))
        for k, v in kwargs.items():
            try:
                func = getattr(self, f"_change_{k}")
            except AttributeError:
                raise ValueError(
                    f"Unsupported change command for field named '{k}' on place with id {id}."
                )
            else:
                try:
                    place = self.apographe[place_id]
                except KeyError:
                    raise ValueError(
                        f"There is no place with id={place_id} in the internal gazetteer list."
                    )
                else:
                    return func(place, v)

    def _change_id(self, place: Place, new_id: str):
        old = place.id
        place.id = new_id
        self.apographe.pop(old)
        self.apographe[new_id] = place
        return f"Changed id of place from {old} to {new_id}."

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
        except KeyError:
            raise ValueError(
                f"There is no place with id={place_key} in the internal gazetteer"
            )
        return place

    def import_file(self, path: str, filetype=None, encoding="utf-8"):
        """Import a file for further processing."""
        filepath = Path(path)
        filepath = filepath.expanduser().resolve()
        ftype = filetype if filetype is not None else filepath.suffix[1:]
        if ftype == "txt":
            with open(filepath, "r", encoding=encoding) as fp:
                data = fp.read()
            del fp
            if "\n" in data:
                data = [l.strip() for l in data.split("\n") if l.strip()]
            filename = filepath.name.split(".")[0]
            slug = slugify(filename)
            self.imports[slug] = data
        else:
            raise NotImplementedError(
                f"Cannot import {path} because filetype: {ftype} if not supported."
            )
        return f"Imported {ftype} file {filepath} and stored data as imports:{slug}."

    def internal(self):
        """List all places in the internal gazetteer."""
        places = [(place_key, place) for place_key, place in self.apographe.items()]
        places.sort(key=lambda x: slugify(x[1].properties.title))
        hits = list()
        for place_key, place in places:
            hits.append(
                {
                    "place_key": place_key,
                    "title": place.properties.title,
                    "uri": place.uri,
                    "summary": place.descriptions.description_strings[0],
                }
            )
        return hits

    def load(self, where: str):
        """Load JSONLPF files at 'where' as places in the internal gazetteer"""
        path = Path(where)
        if len(path.parts) == 1:
            NotImplementedError(where)
        path = path.expanduser().resolve()
        if path.is_dir():
            for filepath in path.glob("*.json"):
                fn = filepath.name
                with open(filepath, "r", encoding="utf-8") as fp:
                    features = load(fp)
                del fp
                places = [Place(**f) for f in features]
                for place in places:
                    for place_id in [
                        place.id,
                        f"{slugify(place.properties.title)}",
                        f"{slugify(fn.split('.')[0])}:{place.id}",
                    ]:
                        try:
                            self.apographe[place_id]
                        except KeyError:
                            self.apographe[place_id] = place
                            break
                    try:
                        self.apographe[place_id]
                    except KeyError:
                        raise RuntimeError()
        return f"Read {len(self.apographe)} places from {str(path)}."

    def save(self, mode: str = "all", where: str = ""):
        """Save the places in the internal gazetteer to the directory at where"""
        filename = None
        dirpath = None
        if where:
            path = Path(where)
            path = path.expanduser()
            if where.endswith(".json") and mode != "each":
                filename = path.parts[-1]
            elif len(path.parts) == 1:
                filename = f"{where}.json"
            elif mode == "all":
                filename = "all.json"
            elif mode not in ["all", "each"]:
                filename = f"{mode}.json"
            if filename:
                if filename == f"{where}.json" and len(path.parts) == 1:
                    # dirpath = user home
                    raise NotImplementedError()
                elif len(path.parts) == 1 and filename == path.parts[0]:
                    # dirpath = user home
                    raise NotImplementedError()
                elif filename == path.parts[-1]:
                    dirpath = path.parent
                else:
                    dirpath = path
        else:
            # dirpath = user home
            raise NotImplementedError()
        dirpath = path.resolve()
        if not dirpath:
            raise RuntimeError()
        dirpath.mkdir(parents=True, exist_ok=True)

        if mode == "all" and dirpath and filename:
            # save all to a single LPF file
            filename = "all.json"
            with open(dirpath / filename, "w", encoding="utf-8") as fp:
                dump(
                    list(self.apographe.values()),
                    fp,
                    ensure_ascii=False,
                    indent=4,
                    sort_keys=True,
                )
            del fp
            return f"Wrote {len(self.apographe)} places to {str(dirpath / filename)}."
        elif mode == "each" and dirpath and not filename:
            # save each place to a separate LPF file
            i = 0
            for place_key, place in self.apographe.items():
                slug = slugify(place_key)
                filename = f"{slug}.json"
                self.logger.debug(f"saving {str(dirpath / filename)}.")
                self.logger.debug(filename)
                with open(dirpath / filename, "w", encoding="utf-8") as fp:
                    dump(place, fp, ensure_ascii=False, indent=4, sort_keys=True)
                del fp
                i += 1
            return f"Wrote {i} files for {len(self.apographe)} places to {str(path)}."
        elif mode and dirpath and filename:
            # save individual to a single file
            raise NotImplementedError()

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

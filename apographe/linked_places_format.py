#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Classes mimicking the structure of the Linked Places Format
https://github.com/LinkedPasts/linked-places-format
"""

from apographe.countries import ccodes_valid, country_names
from apographe.languages_and_scripts import LanguageAware
from apographe.serialization import Serialization, ApographeEncoder
from apographe.text import normtext
from copy import deepcopy
import geojson
import json
import logging
from pathlib import Path
from pprint import pformat
from shapely.geometry import mapping as shapely_mapping
from shapely.geometry import shape as shapely_shape
from slugify import slugify
from uri import URI
from uuid import uuid4
import validators

logger = logging.getLogger(__name__)


def dump(obj, fp, ensure_ascii=True, indent=None, sort_keys=False):
    """Serialize obj to Linked Places Format GeoJSON and save to fp."""
    if not isinstance(obj, Serialization):
        raise TypeError(type(obj))
    fp.write(dumps(obj, ensure_ascii=ensure_ascii, indent=indent, sort_keys=sort_keys))


def dumps(obj, ensure_ascii=True, indent=None, sort_keys=False):
    """Serialize obj to Linked Places Format GeoJSON and return as string."""
    if not isinstance(obj, Serialization):
        raise TypeError(type(obj))
    dumpd = {
        "@context": "https://raw.githubusercontent.com/LinkedPasts/linked-places/master/linkedplaces-context-v1.1.jsonld",
        "type": "FeatureCollection",
        "features": [],
    }
    if isinstance(obj, (list)):
        dumpd["features"].extend(obj)
    elif isinstance(obj, (tuple)):
        dumpd["features"].extend(list(obj))
    else:
        dumpd["features"].append(obj)
    return json.dumps(
        obj=dumpd,
        ensure_ascii=False,
        cls=ApographeEncoder,
        indent=indent,
        sort_keys=sort_keys,
    )


class Name(LanguageAware, Serialization):
    def __init__(self, toponym: str = "", romanizations=[], **kwargs):
        LanguageAware.__init__(self, **kwargs)
        Serialization.__init__(
            self,
            omit=["_name_key", "_language_subtag", "_script_subtag", "_region_subtag"],
        )

        self._romanizations = set()
        self._toponym = None
        self._name_key = None
        if toponym:
            self.toponym = toponym
        if romanizations:
            self.romanizations = romanizations

    def make_key(self):
        if self._name_key:
            return self._name_key
        else:
            try:
                value = list(self._romanizations)[0]
            except IndexError:
                value = self._toponym
            return slugify(value)

    @property
    def name_strings(self):
        strings = deepcopy(self._romanizations)
        strings.add(self._toponym)
        strings = list(strings)
        strings = [s for s in strings if s]
        return strings

    @property
    def romanizations(self):
        return list(self._romanizations)

    @romanizations.setter
    def romanizations(self, values):
        for value in values:
            self.add_romanization(value)

    @romanizations.deleter
    def romanizations(self):
        self._romanizations = set()

    def add_romanization(self, value: str):
        v = normtext(value)
        if v:
            self._romanizations.add(v)

    @property
    def toponym(self):
        return self._toponym

    @toponym.setter
    def toponym(self, value: str):
        v = normtext(value)
        if v:
            self._toponym = v

    @toponym.deleter
    def toponym(self):
        self._toponym = None


class NameCollection(Serialization):
    def __init__(self, names=[], **kwargs):
        Serialization.__init__(self, omit=["_index"], promote="names", refactor=list)
        logger = logging.getLogger(self.__class__.__name__)
        logger.debug(pformat(names, indent=4))
        self._names = dict()
        self._index = dict()
        if names:
            self.names = names

    @property
    def name_strings(self):
        strings = set()
        for n in self.names:
            strings.update(n.name_strings)
        return list(strings)

    @property
    def names(self):
        return list(self._names.values())

    @names.setter
    def names(self, values):
        for name in values:
            self.add_name(name)

    @names.deleter
    def names(self):
        self._names = dict()
        self._index = dict()

    def add_name(self, value):
        if isinstance(value, Name):
            name = value
        elif isinstance(value, dict):
            name = Name(**value)
        elif isinstance(value, str):
            name = Name(toponym=value)
        else:
            raise TypeError(f"Unexpected type for add_name: {type(value)}.")
        name_key = name.make_key()
        try:
            self._names[name_key]
        except KeyError:
            self._names[name_key] = name
        else:
            i = len([k for k in self._names.keys() if k.startswith(name_key)])
            name_key = f"{name_key}-{str(i)}"
            self._names[name_key] = name
        for ns in name.name_strings:
            try:
                self._index[ns]
            except KeyError:
                self._index[ns] = set()
            self._index[ns].add(name_key)

    def get_names(self, s: str):
        try:
            name_keys = self._index[s]
        except KeyError:
            pass
        else:
            return [self._names[k] for k in list(name_keys)]
        s_low = s.lower()
        lower_index = None
        if s_low != s:
            lower_index = {k.lower(): v for k, v in self._index.items()}
            try:
                name_keys = lower_index[s_low]
            except KeyError:
                pass
            else:
                return [self._names[k] for k in list(name_keys)]
        if lower_index is None:
            lower_index = {k.lower(): v for k, v in self._index.items()}
        name_keys = set()
        for k in [k for k in list(lower_index.keys()) if s_low in k]:
            try:
                name_keys.update(lower_index[k])
            except KeyError:
                pass
        return [self._names[k] for k in list(name_keys)]

    def remove_name(self, name: Name):
        if not isinstance(name, Name):
            raise TypeError(f"Unexpected name type {type(name)}.")
        name_key = name.make_key()
        self._names.pop(name_key)
        index_keys = [k for k, v in self._index.items() if name_key in v]
        for k in index_keys:
            self._index[k].remove(name_key)

    def __iter__(self):
        return iter(self._names.values())

    def __len__(self):
        return len(self._names)


class Properties(Serialization):
    def __init__(self, title: str = "", ccodes: list = [], **kwargs):
        Serialization.__init__(self)
        self._title = ""
        self._ccodes = set()

        self.title = title
        self.ccodes = ccodes

    # country codes -- presently lacks validation
    @property
    def ccodes(self):
        return list(self._ccodes)

    @ccodes.setter
    def ccodes(self, ccodes: list = []):
        self._ccodes = set()
        for c in ccodes:
            self.add_ccode(c)

    @property
    def country_names(self):
        return [country_names[c] for c in self.ccodes]

    def add_ccode(self, ccode: str):
        try:
            preferred_code = ccodes_valid[ccode]
        except KeyError:
            raise ValueError(f"Invalid ccode='{ccode}'.")
        logger.info(
            f"Replacing ccode '{ccode}' with corresponding preferred ccode {preferred_code}."
        )
        self._ccodes.add(preferred_code)

    def remove_ccode(self, ccode: str):
        try:
            self._ccodes.remove(ccode)
        except KeyError as original:
            try:
                preferred = ccodes_valid[ccode]
            except KeyError:
                raise original
            else:
                try:
                    self._ccodes.remove(preferred)
                except KeyError:
                    raise original

    # title: arbitrary unicode strings
    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title: str):
        self._title = normtext(title)


class Feature:
    def __init__(self, id: str = None, uri: URI = None, **kwargs):
        self._id_internal = uuid4().hex
        self._id = None
        self._uri = None

        if id:
            self.id = id
        if uri:
            self.uri = uri

        self.properties = Properties(**kwargs)
        self.names = NameCollection(**kwargs)
        try:
            geometries = kwargs["geometries"]
        except KeyError:
            try:
                geometry = kwargs["geometry"]
            except KeyError:
                self.geometry = list()
            else:
                self.geometry = shapely_shape(geometry)
        else:
            if len(geometries) == 1:
                self.geometry = shapely_shape(geometries[0])
            elif len(geometries) > 1:
                geo_collection = [shapely_shape(g) for g in geometries]
                self.geometry = geojson.GeometryCollection(geo_collection)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = normtext(value)

    @property
    def internal_id(self):
        return self._id_internal

    @property
    def uri(self):
        if self._uri is None:
            return None
        return self._uri.uri

    @uri.setter
    def uri(self, value):
        if isinstance(value, str):
            v = normtext(value)
        else:
            v = value
        if v:
            this_uri = URI(v)
            scheme = this_uri.scheme
            if scheme:
                if scheme in ["https", "http"]:
                    if not validators.url(this_uri.uri):
                        raise ValueError(f"Invalid URI: {v}.")
            self._uri = this_uri

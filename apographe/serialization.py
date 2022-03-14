#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Provide dictionary/JSON serialization support
"""

import json
from language_tags.Tag import Tag
from language_tags.Subtag import Subtag
import logging
from pprint import pformat
from shapely.geometry import mapping, Point, LineString, Polygon


class Serialization:
    def __init__(self, omit: list = [], promote: str = "", refactor: type = False):
        self._omit = {"_omit", "_promote", "_refactor"}
        if isinstance(omit, (list, set, tuple)):
            self._omit.update(omit)
        elif isinstance(omit, str):
            self._omit.add(omit)
        self._promote = promote
        self._refactor = refactor

    def asdict(self):
        d = dict()
        for varname, varval in vars(self).items():
            if varname in self._omit:
                continue
            if varname.startswith("_"):
                attrname = varname[1:]
            else:
                attrname = varname
            try:
                attrval = getattr(self, attrname)
            except AttributeError:
                attrval = None
            if varval == attrval:
                val = attrval
            else:
                val = varval
            d[attrname] = self._asdict_process(val)
        if self._promote and len(d) == 1:
            d = d[list(d.keys())[0]]
        elif self._promote:
            raise NotImplementedError(f"promote {pformat(d, indent=4)}")
        if self._refactor == list:
            result = list(d.values())
        elif self._refactor:
            raise NotImplementedError(f"refactor={self._refactor}")
        else:
            result = d
        return result

    def _asdict_process(self, value):

        if isinstance(value, (list, set, tuple)):
            return [self._asdict_process(v) for v in value]
        elif isinstance(value, dict):
            return {k: self._asdict_process(v) for k, v in value.items()}
        elif isinstance(value, (Point, LineString, Polygon)):
            return mapping(value)
        elif isinstance(value, (Tag, Subtag)):
            return value.format
        else:
            return value


class ApographeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Serialization):
            return obj.asdict()
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

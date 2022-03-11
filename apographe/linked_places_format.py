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
from apographe.text import normtext
import json
import logging
from pathlib import Path
from pprint import pformat
from uri import URI
from uuid import uuid4
import validators

logger = logging.getLogger(__name__)


class Name:
    def __init__(self, toponym: str = "", lang: str = ""):
        self._toponym = None
        self._lang = "und"

        if toponym:
            self.toponym = toponym
        if lang:
            self.lang = lang


class Properties:
    def __init__(self, title: str = "", ccodes: list = [], **kwargs):
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

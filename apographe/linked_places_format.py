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
from apographe.text import normtext
import json
import logging
from pathlib import Path
from pprint import pformat
from uri import URI
from uuid import uuid4

logger = logging.getLogger(__name__)

# determine valid country codes/names and their preferred forms
ccodes_path = Path("data/country-codes.json")
ccodes_valid = dict()
with open(ccodes_path, "r", encoding="utf-8") as fp:
    ccodes_data = json.load(fp)
del fp
for entry in ccodes_data:
    for k in [
        "CLDR display name",
        "Geoname ID",
        "ISO3166-1-Alpha-2",
        "ISO3166-1-Alpha-3",
        "ISO3166-1-numeric",
        "MARC",
        "official_name_ar",
        "official_name_cn",
        "official_name_en",
        "official_name_es",
        "official_name_fr",
        "official_name_ru",
        "UNTERM Arabic Formal",
        "UNTERM Arabic Short",
        "UNTERM Chinese Formal",
        "UNTERM Chinese Short",
        "UNTERM English Formal",
        "UNTERM English Short",
        "UNTERM French Formal",
        "UNTERM French Short",
        "UNTERM Russian Formal",
        "UNTERM Russian Short",
        "UNTERM Spanish Formal",
        "UNTERM Spanish Short",
    ]:
        value = None
        preferred = None

        value = entry[k]
        if not value:
            continue
        if not isinstance(value, str):
            continue
        if "," in value:
            logger.debug(f"skipping {k} == '{value}'")
            continue
        if k == "MARC" and value in {"uik"}:
            continue

        preferred = entry["ISO3166-1-Alpha-2"]
        if not preferred:
            continue
        if "," in preferred:
            logger.debug(f"skipping ISO3166-1-Alpha-2 == '{preferred}'")
            continue

        try:
            ccodes_valid[value]
        except KeyError:
            ccodes_valid[value] = preferred
        else:
            if ccodes_valid[value] != preferred:
                raise RuntimeError(
                    f"collision: '{value}' currently == {ccodes_valid[value]} failed == {preferred}"
                )
del ccodes_data
del ccodes_path


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
        self._ccodes.pop(ccode)

    # title: arbitrary unicode strings
    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title: str):
        self._title = normtext(title)


class Feature:
    def __init__(self, id: str = "", uri: URI = None, **kwargs):
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
    def uri(self, value):
        return self._uri.uri

    @property
    def internal_id(self):
        return self._id_internal

    @uri.setter
    def uri(self, value):
        if isinstance(value, str):
            v = normtext(value)
        else:
            v = value
        if v:
            self._uri = URI(value)

#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Define and manage country-related metadata
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


# determine valid country codes/names and their preferred forms
ccodes_path = Path("data/country-codes.json")
ccodes_valid = dict()
country_names = dict()
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
        "UNTERM Arabic Short",
        "UNTERM Chinese Short",
        "UNTERM English Short",
        "UNTERM French Short",
        "UNTERM Russian Short",
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

        if k == "ISO3166-1-Alpha-2":
            name = entry["official_name_en"]
            if name:
                country_names[value] = name
del ccodes_data
del ccodes_path

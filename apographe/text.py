#
# This file is part of pleiades_search_api
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#
"""
Utilities for working with text
"""

import logging
from textnorm import normalize_space, normalize_unicode

logger = logging.getLogger(__name__)


def normtext(s: str):
    return normalize_space(normalize_unicode(s))

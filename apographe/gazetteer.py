#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Base class for gazetteers
"""

import logging

logger = logging.getLogger(__name__)


class Gazetteer:
    """Base mixin for providing functionality common to gazetteers."""

    def __init__(self, name: str):
        self.name = name

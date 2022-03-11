#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Base class for gazetteers
"""

from apographe.place import Place


class Gazetteer:
    """Base mixin for providing functionality common to gazetteers."""

    def __init__(self, name: str):
        self.name = name

    def make_place(self, id: str, raw: dict):
        """Create a standardized place object"""
        # override this method for each gazetteer
        return Place(id, raw)

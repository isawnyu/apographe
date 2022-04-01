#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Define Place class
"""
from apographe.linked_places_format import Feature
from apographe.serialization import Serialization
import logging
from pprint import pformat


class Place(Feature, Serialization):
    def __init__(self, raw=None, **kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug(pformat(kwargs, indent=4))
        Serialization.__init__(self, omit=["raw", "logger"])
        self.raw = raw
        Feature.__init__(self, **kwargs)

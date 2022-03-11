#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Gazetteer Inferface for the Pleiades gazetteer of ancient places
"""

from apographe.gazetteer import Gazetteer
from apographe.place import Place
from apographe.web import BackendWeb
import logging

logger = logging.getLogger(__name__)


class Pleiades(BackendWeb, Gazetteer):
    def __init__(self):
        Gazetteer.__init__(self, name="Pleiades")
        kwargs = {
            "place_netloc": "pleiades.stoa.org",
            "place_scheme": "https",
            "place_path": "/places/",
            "place_suffix": "/json",
            "user_agent": "ApographeTester/0.0.1 (+https://github.org/isawnyu/apographe)",
        }
        BackendWeb.__init__(self, **kwargs)

    def make_place(self, id: str, raw: dict):
        return PleiadesPlace(id, raw)


class PleiadesPlace(Place):
    def __init__(self, id: str, raw: dict):
        Place.__init__(self, id, raw)

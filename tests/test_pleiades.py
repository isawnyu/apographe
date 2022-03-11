#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Test the apographe.pleiades module
"""

from apographe.pleiades import Pleiades
from apographe.web import BackendWeb


class TestPleiades:
    p = Pleiades()

    def test_init(self):
        # Pleiades should have a web backend
        self.p.backend = "web"


class TestPleiadesWeb:
    """
    Test Pleiades functionality using the web backend.
    """

    p = Pleiades()

    def test_get_web(self):
        self.p.backend = "web"
        place = self.p.get("295374")
        assert place.raw["title"] == "Zucchabar"

#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Test the apographe.web module
"""

from apographe.web import BackendWeb
import pytest
from webiquette.webi import Webi


class TestBackendWeb:
    wb = None

    def test_web(self):
        kwargs = {
            "place_netloc": "pleiades.stoa.org",
            "place_scheme": "https",
            "place_path": "/places/",
            "place_suffix": "/json",
            "user_agent": "ApographeTester/0.0.1 (+https://github.org/isawnyu/apographe)",
        }
        self.wb = BackendWeb(**kwargs)
        assert self.wb._backend_supported("web")
        config = self.wb._backends["web"]
        for k, v in kwargs.items():
            assert config[k] == v
        assert isinstance(config["place_interface"], Webi)
        assert config["get"]
        # search TBD
        self.wb.backend = "web"

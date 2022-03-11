#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Test the apographe.query module
"""

from apographe.query import Query
import pytest


class TestQuery:
    def test_query(self):
        q = Query()
        assert q.supported_parameters == list()
        assert q.parameters_for_web == dict()
        with pytest.raises(ValueError):
            q.set_parameter("foo", "bar")

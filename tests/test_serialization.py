#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Test the apographe.serialization module
"""

from apographe.place import Place
from apographe.serialization import ApographeEncoder, Serialization
import json


class Mock(Serialization):
    def __init__(self):
        self.foo = "bar"
        Serialization.__init__(self)


class TestSerialization:
    def test_base(self):
        o = Serialization()
        d = o.asdict()
        assert len(d) == 0

    def test_mock(self):
        o = Mock()
        d = o.asdict()
        assert len(d) == 1
        j = json.dumps(d, cls=ApographeEncoder)
        assert j == '{"foo": "bar"}'

#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Test the apographe.backend module
"""

from apographe.backend import Backend
import pytest


class TestBackend:
    b = Backend()

    def test_init(self):
        b = self.b
        assert b._current_backend is None
        assert isinstance(b._backends, dict)
        assert len(b._backends) == 0

    def test_current_unsupported(self):
        b = self.b
        with pytest.raises(RuntimeError):
            b.backend = "foo"

    def test_current_supported(self):
        b = self.b
        b._backends["foo"] = "bar"  # pretend there is a backend called "foo"
        b.backend = "foo"
        assert len(b._backends) == 1
        assert list(b._backends.keys())[0] == "foo"

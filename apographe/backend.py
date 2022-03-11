#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Mixin to provide basic backend support for a gazetteer
"""


from sqlite3 import NotSupportedError


class Backend:
    def __init__(self):
        try:
            self._backends
        except AttributeError:
            self._backends = dict()
        self._current_backend = None

    @property
    def backend(self):
        return self._current_backend

    @backend.setter
    def backend(self, backend: str):
        try:
            self._backends[backend]
        except KeyError:
            raise RuntimeError(
                f"Unsupported backend: {backend}. Available: {', '.join(list(self._backends.keys()))}"
            )

    @backend.deleter
    def backend(self):
        self._current_backend = None

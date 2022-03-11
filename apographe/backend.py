#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Mixin to provide basic backend support for a gazetteer
"""


from xml.dom.minidom import Attr


class Backend:
    def __init__(self):
        try:
            self._backends
        except AttributeError:
            self._backends = dict()
        try:
            self._current_backend
        except AttributeError:
            self._current_backend = None

    @property
    def backend(self):
        """Report the name of the currently enabled backend"""
        return self._current_backend

    @backend.setter
    def backend(self, backend: str):
        """Set the currently enabled backend by name"""
        if self._backend_supported(backend):
            self._current_backend = backend

    def configure_backend(self, backend: str, config: dict):
        """Store configuration data for a named backend"""
        if self._backend_supported(backend):
            self._backends[backend] = config

    def _backend_supported(self, backend: str):
        """Raise RuntimeError if named backend has not been registered"""
        try:
            self._backends[backend]
        except KeyError:
            raise RuntimeError(
                f"Unsupported backend: {backend}. Available: {', '.join(list(self._backends.keys()))}"
            )
        return True

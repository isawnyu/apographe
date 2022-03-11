#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Define Place class
"""


class Place:
    def __init__(self, id: str, raw=None):
        self.id = id
        self.raw = raw
        if isinstance(raw, dict):
            fields = {"title": "title"}
            for key, attrname in fields.items():
                try:
                    v = raw[key]
                except KeyError:
                    continue
                else:
                    setattr(self, attrname, v)

#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Metadata, vocabularies, and utilities for languages and scripts
"""
from language_tags import tags


class LanguageAware:
    """A mixin base class for making types language-aware."""

    def __init__(self, **kwargs):
        self._language_tag = None
        self._language_subtag = None
        self._script_subtag = None
        self._region_subtag = None

        for k, v in kwargs.items():
            try:
                setattr(self, k, v)
            except AttributeError:
                pass

    @property
    def language_tag(self):
        if self._language_tag:
            return self._language_tag.format
        else:
            return "und"

    @language_tag.setter
    def language_tag(self, value: str):
        tag = tags.tag(value)
        if tag.valid:
            self._language_tag = tag
            self._language_subtag = tag.language
            self._region_subtag = tag.region
            self._script_subtag = tag.script
            if self._script_subtag is None:
                self._script_subtag = self._language_subtag.script
        else:
            # eventually try to fix this
            raise ValueError(
                f"Invalid language tag '{value}': {'; '.join([str(e) for e in tag.errors])}"
            )

    @property
    def language_subtag(self):
        try:
            return self._language_subtag.format
        except AttributeError:
            return None

    @property
    def region_subtag(self):
        try:
            return self._region_subtag.format
        except AttributeError:
            return None

    @property
    def script_subtag(self):
        try:
            return self._script_subtag.format
        except AttributeError:
            return None

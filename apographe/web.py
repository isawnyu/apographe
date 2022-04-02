#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#

"""
Mixin to provide a web-based backend for a gazetteer
"""

from apographe.backend import Backend
from apographe.text import normtext
from copy import deepcopy
import logging
from urllib.parse import urlencode, urlunparse
import validators
from webiquette.webi import Webi, DEFAULT_HEADERS

DEFAULT_SCHEME = "https"
DEFAULT_USER_AGENT = "Apographe/0.0.1 (+https://github.com/isawnyu/apographe)"

logger = logging.getLogger("apographe.web")


class BackendWeb(Backend):
    """Base mixin for providing web-aware backend functionality for gazetteers."""

    def __init__(
        self,
        place_netloc: str = None,
        place_scheme: str = DEFAULT_SCHEME,
        place_path: str = "/",
        place_suffix: str = "",
        search_netloc: str = None,
        search_scheme: str = DEFAULT_SCHEME,
        search_path: str = "/",
        user_agent=DEFAULT_USER_AGENT,
        **kwargs,
    ):
        web_config = dict()

        # determine scheme
        expected_schemes = ["http", "https"]
        if place_scheme not in expected_schemes:
            raise ValueError(
                f"Web backend expected place_scheme in {expected_schemes}. Got '{place_scheme}'."
            )
        else:
            web_config["place_scheme"] = place_scheme
        if search_scheme not in expected_schemes:
            raise ValueError(
                f"Web backend expected search_scheme in {expected_schemes}. Got '{search_scheme}'."
            )
        else:
            web_config["search_scheme"] = search_scheme

        # determine path components for place and search
        web_config["place_path"] = place_path
        web_config["place_suffix"] = place_suffix
        web_config["search_path"] = search_path

        # determine standard HTTP headers
        place_headers = deepcopy(DEFAULT_HEADERS)
        ua = None
        try:
            ua = normtext(user_agent)
        except TypeError:
            pass
        if not ua:
            ua = DEFAULT_USER_AGENT
        if ua == DEFAULT_USER_AGENT:
            logger.warning(
                f'Using default HTTP Request header for User-Agent = "{ua}". '
                "We strongly prefer you define your own unique user-agent string."
            )
        web_config["user_agent"] = ua
        place_headers["User-Agent"] = ua
        try:
            place_headers["accept"] = kwargs["accept"]
        except KeyError:
            pass
        web_kwargs = dict()
        if kwargs:
            for k, v in kwargs.items():
                if k in {"respect_robots_txt", "cache_control", "expire_after"}:
                    web_kwargs[k] = v

        # determine netlocs (domains)
        if not validators.domain(place_netloc):
            raise ValueError(
                f"Web backend expects a valid domain for place_netloc. Got '{place_netloc}."
            )
        web_config["place_netloc"] = place_netloc
        if not validators.domain(search_netloc):
            raise ValueError(
                f"Web backend expects a valid domain for search_netloc. Got '{search_netloc}."
            )
        web_config["search_netloc"] = search_netloc

        web_config["place_interface"] = Webi(
            netloc=place_netloc, headers=place_headers, **web_kwargs
        )
        web_config["search_interface"] = Webi(
            netloc=search_netloc,
            headers=place_headers,
            **web_kwargs,  # may need to differentiate this for search
        )

        web_config["get"] = self._web_get
        web_config["search"] = self._web_search

        Backend.__init__(self)
        self.configure_backend("web", web_config)

    def search(self, query_uri: str):
        return Backend.search(self, query_uri)

    def _prep_params(self, **kwargs):
        """Prepare params for web query"""
        ready_kwargs = dict()
        for k, v in kwargs.items():
            if v is None:
                ready_kwargs[k] = ""
            elif isinstance(v, str):
                ready_kwargs[k] = v
            elif isinstance(v, list):
                if k in ["getFeatureType", "Subject:list"]:
                    ready_kwargs[k] = v
                else:
                    ready_kwargs[f"{k}:list"] = ",".join(v)
            else:
                raise TypeError(type(v))
        params = urlencode(ready_kwargs, doseq=True)
        return params

    def _web_get(self, id: str):
        """HTTP GET using caching, robots:crawl-delay, etc."""
        config = self.backend_configuration("web")
        uri = urlunparse(
            (
                f"{config['place_scheme']}",
                config["place_netloc"],
                f"{config['place_path']}{id}{config['place_suffix']}",
                "",
                "",
                "",
            )
        )
        return config["place_interface"].get(uri)

    def _web_search(self, query: str):
        """Issue the search"""
        config = self.backend_configuration("web")
        try:
            if not validators.url(query):
                raise ValueError(f"Expected a valid search URI but got '{query}'.")
        except TypeError:
            raise TypeError(
                f"Expected a query argument of type {str} but got {type(query)}."
            )
        return config["search_interface"].get(query)

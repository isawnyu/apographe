#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Get places from a gazetteer
"""

from airtight.cli import configure_commandline
from apographe.pleiades import Pleiades, PleiadesQuery
import logging
from pprint import pprint

logger = logging.getLogger(__name__)

DEFAULT_LOG_LEVEL = logging.WARNING
OPTIONAL_ARGUMENTS = [
    ["-b", "--backend", "web", "Backend to use for query", False],
    ["-g", "--gazetteer", "pleiades", "Name of gazetteer to query", False],
    [
        "-l",
        "--loglevel",
        "NOTSET",
        "desired logging level ("
        + "case-insensitive string: DEBUG, INFO, WARNING, or ERROR",
        False,
    ],
    ["-t", "--tags", "NOTSET", "comma-separated list of tags to use", False],
    ["-v", "--verbose", False, "verbose output (logging level == INFO)", False],
    [
        "-w",
        "--veryverbose",
        False,
        "very verbose output (logging level == DEBUG)",
        False,
    ],
]
POSITIONAL_ARGUMENTS = [
    # each row is a list with 3 elements: name, type, help
]


def main(**kwargs):
    """
    main function
    """
    # logger = logging.getLogger(sys._getframe().f_code.co_name)
    if kwargs["gazetteer"].lower() == "pleiades":
        gaz = Pleiades()
    else:
        raise NotImplementedError(kwargs["gazetteer"])
    if kwargs["backend"].lower() == "web":
        gaz.backend = kwargs["backend"]
    else:
        raise NotImplementedError(kwargs["backend"])
    q = PleiadesQuery()
    supported_query_params = ["tags"]
    for k, v in kwargs.items():
        if k in ["gazetteer", "backend", "loglevel", "verbose", "veryverbose"]:
            continue
        if "," in v:
            vv = v.split(",")
        else:
            vv = v
        if k in supported_query_params:
            if k == "tags":
                q.set_parameter("tag", vv)
            else:
                q.set_parameter(k, vv)
        else:
            raise NotImplementedError(k)
    results = gaz.search(q)
    pprint(results["hits"], indent=4)


if __name__ == "__main__":
    main(
        **configure_commandline(
            OPTIONAL_ARGUMENTS, POSITIONAL_ARGUMENTS, DEFAULT_LOG_LEVEL
        )
    )

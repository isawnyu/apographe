#
# This file is part of apographe
# by Tom Elliott for the Institute for the Study of the Ancient World
# (c) Copyright 2022 by New York University
# Licensed under the AGPL-3.0; see LICENSE.txt file.
#
"""
geographic utilities
"""

import logging
from math import asin, atan2, cos, degrees, pi, radians, sin
from os import minor
from shapely.geometry import LineString, Point
from shapely.ops import unary_union

logger = logging.getLogger(__name__)


def bubble(
    origin_shape,
    buffer_distance=0,
    radius_multiplier=1,
    radius_minimum=1,
    radius_maximum=10000,
):
    """
    Calculate a buffered bubble around a shape.
    origin_shape is assumed to have WGS84 lon/lat coordinates.
    buffer_distance and radius_minimum are in meters.
    returned shape is in WGS84 lat/lon
    """
    origin = origin_shape.centroid
    origin_lon = radians(origin.x)
    origin_lat = radians(origin.y)
    distance = max(
        origin_shape.length / 2 * radius_multiplier + buffer_distance, radius_minimum
    )
    earth_radius = 6378137.0  # WGS84 mean radius
    angular_distance = distance / earth_radius
    termini = list()
    bearing = 0.0
    while True:
        if bearing >= 2.0 * pi:
            break
        dest_lat = asin(
            sin(origin_lat) * cos(angular_distance)
            + cos(origin_lat) * sin(angular_distance) * cos(bearing)
        )
        dest_lon = origin_lon + atan2(
            sin(bearing) * sin(angular_distance) * cos(origin_lat),
            cos(angular_distance) - sin(origin_lat) * sin(dest_lat),
        )
        termini.append(Point(degrees(dest_lon), degrees(dest_lat)))
        bearing += pi / 19.0
    for t in termini:
        logger.debug(f"terminus: {t.wkt}")
    if isinstance(origin_shape, Point):
        bub = unary_union(termini).convex_hull
    else:
        d_dd = max([t.hausdorff_distance(origin_shape) for t in termini])
        bub = origin_shape.convex_hull.buffer(d_dd)
    return bub


def axes(origin_shape):
    mbr_points = list(zip(*origin_shape.minimum_rotated_rectangle.exterior.coords.xy))
    mbr_lengths = [
        LineString((mbr_points[i], mbr_points[i + 1])).length
        for i in range(len(mbr_points) - 1)
    ]
    minor_axis = round(min(mbr_lengths), 2)
    major_axis = round(max(mbr_lengths), 2)
    return (major_axis, minor_axis)

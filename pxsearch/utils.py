import io
import logging
import math

import rasterio
from dateutil import parser
from dateutil.relativedelta import relativedelta
from rasterio import Affine
from rasterio.crs import CRS
from rasterio.enums import Resampling
from rasterio.features import bounds, rasterize
from rasterio.warp import transform

logger = logging.getLogger(__name__)


def compute_wgs84_bbox(geojson, return_bbox=False):
    """
    Computes the bounding box of the input geojson in WGS84 coordinates.

    Parameters
    ----------
    gejson : dict
        Geometric data from which to compute a bounding box.
    return_bbox : bool or None, optional
        If True, a simple bbox tuple is returned (xmin, ymin, xmax, ymax). If
        False, the bbox is returned as geojson polygon feature.

    Returns
    -------
    bbox : tuple or dict
        The bounding box of the input geometry. Either as tuple or geojson
        feature.
    """
    # Compute bounding box in original coordinates.
    bbox = bounds(geojson)
    # Get crs string from geojson.
    crs = (
        geojson["crs"]["init"]
        if "init" in geojson["crs"]
        else geojson["crs"]["properties"]["name"]
    )
    # Transform the bbox if necessary.
    if crs != "EPSG:4326":
        # Setup crs objects for source and destination.
        src_crs = CRS({"init": crs})
        dst_crs = CRS({"init": "EPSG:4326"})
        # Compute transformed coordinates.
        transformed_coords = transform(
            src_crs, dst_crs, (bbox[0], bbox[2]), (bbox[1], bbox[3])
        )
        # Set bbox from output.
        bbox = (
            transformed_coords[0][0],
            transformed_coords[1][0],
            transformed_coords[0][1],
            transformed_coords[1][1],
        )

    if not return_bbox:
        # Convert bounding box to geojson polygon.
        bbox = {
            "type": "Polygon",
            "coordinates": [
                [
                    [bbox[0], bbox[1]],
                    [bbox[0], bbox[3]],
                    [bbox[2], bbox[3]],
                    [bbox[2], bbox[1]],
                    [bbox[0], bbox[1]],
                ]
            ],
        }

    return bbox

# Creates polygon from bbox.
def generate_polygon(bbox):
    """
    Generates a polygon in the geojson format.
    Parameters
    ----------
        bbox: list
        List of Coordinates. The coordinates must be in WGS84.
    Returns
    -------
    pol: dict, geojson
    Returns a dict with coordinates of AOI.
    """
    pol = {
        "crs": {"init": "EPSG:4326"},
        "type": "Polygon",
        "coordinates": [
            [
                [bbox[0], bbox[1]],
                [bbox[2], bbox[1]],
                [bbox[2], bbox[3]],
                [bbox[0], bbox[3]],
                [bbox[0], bbox[1]],
            ]
        ],
    }

    return pol

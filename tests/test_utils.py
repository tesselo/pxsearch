import datetime
import tempfile
import unittest

import numpy
import rasterio

from pxsearch.utils import (
    compute_wgs84_bbox
)


class TestUtils(unittest.TestCase):
    def setUp(self):
        # Create temp geojson
        self.geojson = {
            "type": "FeatureCollection",
            "crs": {"init": "EPSG:3857"},
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [-1020256.0, 4680156.0],
                                [-1020256.0, 4680000.0],
                                [-1020000.0, 4680000.0],
                                [-1020000.0, 4680156.0],
                                [-1020256.0, 4680156.0],
                            ]
                        ],
                    },
                },
            ],
        }

    def test_compute_wgs84_bbox(self):
        # Geojson feature case.
        bbox = compute_wgs84_bbox(self.geojson)
        expected = [
            [
                [-9.165115585146461, 38.70848390053471],
                [-9.165115585146461, 38.70957743561777],
                [-9.162815898019115, 38.70957743561777],
                [-9.162815898019115, 38.70848390053471],
                [-9.165115585146461, 38.70848390053471],
            ]
        ]
        self.assertEqual(bbox["type"], "Polygon")
        numpy.testing.assert_almost_equal(bbox["coordinates"], expected)
        # BBox case.
        bbox = compute_wgs84_bbox(self.geojson, return_bbox=True)
        expected = (
            -9.165115585146461,
            38.70848390053471,
            -9.162815898019115,
            38.70957743561777,
        )
        numpy.testing.assert_almost_equal(bbox, expected)

from sqlalchemy import create_engine

from pxsearch.utils import get_connection_url


def create_imagery_view():

    engine = create_engine(get_connection_url())

    # Query definition
    definition = """CREATE OR REPLACE VIEW data.imagery AS
    SELECT collection_id,
    id AS "product_id",
    geometry AS "bbox",
    datetime::timestamp AS "sensing_time",
    properties->>'platform' AS "spacecraft_id",
    properties->>'instruments' AS "sensor_id",
    properties->>'proj:transform' AS "proj_transform",
    properties->>'landsat:wrs_row' AS "wrs_row",
    properties->>'landsat:wrs_path' AS "wrs_path",
    CAST(properties->>'landsat:cloud_cover_land' AS NUMERIC) AS "cloud_cover",
    properties->>'granule_id' AS "granule_id",
    properties->>'mgrs_tile' AS "mgrs_tile",
    assets AS "links",
    y.x->'href' AS "base_url"
    FROM data.items jt,
    LATERAL (SELECT jsonb_array_elements(links) x) y
    WHERE y.x @> '{"rel": "self"}';
    """

    engine.execute(definition)


def drop_imagery_view():
    engine = create_engine(get_connection_url())
    engine.execute("DROP VIEW data.imagery")

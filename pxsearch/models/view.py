from pxsearch.utils import get_connection_url
from sqlalchemy import create_engine


def create_imagery_view():
        
    engine = create_engine(get_connection_url())


    #Query definition
    definition = """CREATE OR REPLACE VIEW data.imagery AS 
    SELECT collection_id, 
    geometry AS "bbox",
    datetime::timestamp AS "sensing_time", 
    properties->>'platform' AS "platform", 
    properties->>'instruments' AS "sensor_id", 
    properties->>'proj:transform' AS "proj_transform", 
    properties->>'landsat:wrs_row' AS "wrs_row", 
    properties->>'landsat:wrs_path' AS "wrs_path", 
    properties->>'landsat:cloud_cover_land' AS "cloud_cover",
    y.x->'href' AS "base_url" FROM data.items jt, LATERAL (SELECT jsonb_array_elements(links) x) y WHERE y.x @> '{"rel": "self"}';
    """

    engine.execute(definition)

import json

import structlog
from botocore.exceptions import ClientError

from pxsearch.db import session
from pxsearch.ingest.utils import instantiate_items, open_usgs_landsat_file

logger = structlog.get_logger(__name__)


def ingest_usgs_signal(event, context):
    """
    Ingest data from an usgs-landsat bucket event.
    """
    message = json.loads(event["Records"][0]["Sns"]["Message"])
    location = message["s3_location"]
    product = message["landsat_product_id"]
    logger.debug(f"Ingesting landsat scene {product}")
    key = f"{location}{product}_stac.json".replace("s3://usgs-landsat/", "")
    try:
        item_json_str = open_usgs_landsat_file(key).read().decode("utf-8")
    except ClientError:
        print(message)
        print(key)
        raise
    item_json = json.loads(item_json_str)

    items = instantiate_items([item_json])
    session.bulk_save_objects(items)
    session.commit()


def ingest_s2_signal(event, context):
    """
    Ingest data from a S2 L2A bucket event.
    """
    item = json.loads(event["Records"][0]["Sns"]["Message"])
    logger.debug(f"Ingesting sentinel scene {item['id']}")
    items = instantiate_items([item])
    session.bulk_save_objects(items)
    session.commit()

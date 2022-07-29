import json

import sentry_sdk
import structlog

from pxsearch.db import session
from pxsearch.db_fixtures import pg_on_conflict_do_nothing  # noqa: F401
from pxsearch.ingest.const import SENTINEL_2_SNS_ARN, USGS_SNS_ARN
from pxsearch.ingest.utils import (
    instantiate_items,
    list_usgs_landsat_stac_items,
    open_usgs_landsat_file,
)

logger = structlog.get_logger(__name__)


def signal_handler(event, context):
    try:
        arn = event["Records"][0]["Sns"]["TopicArn"]

        if arn == SENTINEL_2_SNS_ARN:
            ingest_s2_signal(event)
        elif arn == USGS_SNS_ARN:
            ingest_usgs_signal(event)
        else:
            raise ValueError(f"Could not handle SNS event {event}")
    except Exception as e:
        logger.error(
            "Captured Exception in the all catching signal_handler",
            exception=e,
        )
        sentry_sdk.capture_exception(e)
        raise e


def ingest_usgs_signal(event):
    """
    Ingest data from an usgs-landsat bucket event.
    """
    message = json.loads(event["Records"][0]["Sns"]["Message"])
    prefix = message["s3_location"].replace("s3://usgs-landsat/", "")
    stac_item_uris = list_usgs_landsat_stac_items(prefix)

    stac_item_jsons = []
    for item in stac_item_uris:
        item_json_str = open_usgs_landsat_file(item).read().decode("utf-8")
        item_json = json.loads(item_json_str)
        stac_item_jsons.append(item_json)

    items = instantiate_items(stac_item_jsons)
    session.bulk_save_objects(items)
    session.commit()


def ingest_s2_signal(event):
    """
    Ingest data from a S2 L2A bucket event.
    """
    item = json.loads(event["Records"][0]["Sns"]["Message"])
    logger.debug(f"Ingesting sentinel scene {item['id']}")
    items = instantiate_items([item])
    session.bulk_save_objects(items)
    session.commit()

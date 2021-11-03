import json
import logging
from datetime import datetime
from multiprocessing import Pool

import boto3
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import Insert

from pxsearch import const
from pxsearch.db import session
from pxsearch.models.stac import Collection, Item

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


@compiles(Insert, "postgresql")
def postgresql_on_conflict_do_nothing(insert, compiler, **kw):
    """
    Override insert statement to ignore duplicate primary key conflicts. This
    allows running this script against a database that already has some data
    populated.
    https://github.com/sqlalchemy/sqlalchemy/issues/5374#issuecomment-752693165
    """
    statement = compiler.visit_insert(insert, **kw)
    # IF we have a "RETURNING" clause, we must insert before it
    returning_position = statement.find("RETURNING")
    if returning_position >= 0:
        return (
            statement[:returning_position]
            + "ON CONFLICT DO NOTHING "
            + statement[returning_position:]
        )
    else:
        return statement + " ON CONFLICT DO NOTHING"


def create_collections():
    """
    Save all LS collections in the DB.
    """
    collections = []
    for collection_id in const.LS_COLLECTIONS:
        logger.info(f"Instanciating collection {collection_id}")
        s3 = boto3.client("s3")
        collection = s3.get_object(
            Bucket=const.LS_BUCKET_NAME,
            Key=f"collection02/{collection_id}.json",
            RequestPayer="requester",
        )
        collection = collection["Body"].read()
        collection = collection.decode("utf-8")
        collection = json.loads(collection)
        collection = Collection(
            id=collection["id"],
            stac_version=collection["stac_version"],
            stac_extensions=collection["stac_extensions"],
            title=collection["title"],
            description=collection["description"],
            keywords=collection["keywords"],
            license=collection["license"],
            providers=collection["providers"],
            summaries=collection["summaries"],
            extent=collection["extent"],
            links=collection["links"],
            type=collection["type"],
        )
        collections.append(collection)
    logger.info(f"Saving {len(collections)} collections")
    session.bulk_save_objects(collections)
    session.commit()
    logger.info("Collections saved.")


def build_item_from_key(key):
    """
    Download item data and instanciate item class with data.
    """
    # Get metadata from JSON file on S3.
    logger.debug(f"Getting object {key}")
    s3 = boto3.client("s3")
    item_object = s3.get_object(
        Bucket=const.LS_BUCKET_NAME,
        Key=key,
        RequestPayer="requester",
    )
    item_body = item_object["Body"].read().decode("utf-8")
    item = json.loads(item_body)

    # Ensure the type is feature.
    if item["type"] != "Feature":
        raise ValueError(f"Item type must be Feature, found {item['type']}")

    return Item(
        id=item["id"],
        stac_version=item["stac_version"],
        stac_extensions=item["stac_extensions"],
        geometry=json.dumps(item.pop("geometry")),
        bbox=item["bbox"],
        properties=item["properties"],
        assets=item["assets"],
        collection_id=item["collection"],
        parent_collection=item.get("parent_collection", None),
        datetime=datetime.strptime(
            item["properties"]["datetime"], const.DATETIME_RFC339
        ),
        links=item["links"],
    )


def ingest_LS_L2_bucket_items(section, year, path=None):
    """
    Ingest Landsat L2 data for a collection and year.
    """
    batch = []
    counter = 0
    logger.info("Registering items")
    for stac_key in loop_through_files(section, year, path):
        if stac_key is None:
            continue
        counter += 1
        batch.append(stac_key)
        # Continue adding more item keys to batch until batch size is reached.
        if len(batch) < const.INGESTION_BATCH_SIZE:
            continue
        batch = process_batch(batch)
    # Commit remaining items.
    if len(batch):
        process_batch(batch)


def process_batch(batch):
    """
    Commit a list of items to the database.
    """
    logger.info("Downloading item data for batch")
    # Get item data.
    if len(batch) > 1:
        with Pool(min(const.INGESTION_BATCH_SIZE, len(batch))) as pl:
            items = pl.map(build_item_from_key, batch)
    else:
        items = [build_item_from_key(batch[0])]
    logger.info("Downloading item data for batch complete")
    # Save items to DB.
    logger.info(f"Commiting {len(items)} items")
    session.bulk_save_objects(items)
    session.commit()
    logger.info("Commiting items done")
    # Clear batch list.
    batch = []
    return batch


def get_iterator(prefix):
    """
    Get a filtered iterator for a prefix. The iterator will be filtered to stac
    item data keys.
    """
    client = boto3.client(const.CLIENT_TYPE)
    paginator = client.get_paginator(const.PAGINATOR_LOOKUP)
    iterator = paginator.paginate(
        Bucket=const.LS_BUCKET_NAME, Prefix=prefix, RequestPayer="requester"
    )
    filtered_iterator = iterator.search(const.LS_L2_STAC_ITEM_FILE_JMES_SEARCH)
    return filtered_iterator


def loop_through_files(section, year, path=None):
    """
    Yield all STAC item json data keys in a section of the LS L2 bucket.
    """
    # Check input.
    if section not in ["etm", "oli-tirs", "tm"]:
        raise ValueError(f"Section {section} unknown.")
    if year not in range(1982, 2025):
        raise ValueError(f"Year {year} unknown.")
    if path is not None and path not in range(const.WRS_PATH_MAX):
        raise ValueError(f"Path {path} unknown.")
    # Prepare iterator for this section of the data.
    prefix = f"{const.LS_L2_PAGINATOR_BASE_PREFIX}{section}/{year}/"
    if path is not None:
        prefix = f"{prefix}{str(path).zfill(3)}/"
    logger.info(f"Searching for stac items under {prefix}")
    filtered_iterator = get_iterator(prefix)
    # Yield all STAC json keys in this section.
    for stac_key in filtered_iterator:
        yield stac_key


def process_ls_sns_payload(payload):
    """
    Ingest a single STAC item based on a
    """
    message = json.loads(payload["Records"][0]["Sns"]["Message"])
    s3_location = message["s3_location"]
    prefix = s3_location.split(f"s3://{const.LS_BUCKET_NAME}/")[1]
    filtered_iterator = get_iterator(prefix)
    batch = [result for result in filtered_iterator]
    process_batch(batch)

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


def get_keys(prefix):
    s3 = boto3.client("s3")
    paginator = s3.get_paginator(const.PAGINATOR_LOOKUP)
    for result in paginator.paginate(
        Bucket=const.LS8_L2_BUCKET_NAME,
        Prefix=prefix,
        Delimiter="/",
        RequestPayer="requester",
    ):
        if result.get("CommonPrefixes") is None:
            continue
        for key in result.get("CommonPrefixes"):
            yield key.get("Prefix")


def get_ls8_l2_keys_manual():
    for year in range(2013, 2021):
        for path in range(164, 171):
            for row in range(67, 80):
                latkey = "{base}{year}/{path}/{row}".format(
                    base=const.LS8_L2_PAGINATOR_BASE_PREFIX,
                    year=year,
                    path=str(path).zfill(3),
                    row={str(row).zfill(3)},
                )
                for scenekey in get_keys(latkey):
                    yield scenekey


def get_ls8_l2_keys():
    for year in range(2013, 2021):
        for path in range(1, const.WRS_PATH_MAX + 1):
            pathkey = "{base}{year}/{path}".format(
                base=const.LS8_L2_PAGINATOR_BASE_PREFIX,
                year=year,
                path=str(path).zfill(3),
            )
            logger.info(f"Path key {pathkey}")
            for row in range(1, const.WRS_ROW_MAX + 1):
                rowkey = f"{pathkey}{str(row).zfill(3)}/"
                # for rowkey in get_keys(pathkey):
                logger.info(f"Row key {rowkey}")
                for scenekey in get_keys(rowkey):
                    logger.info(f"Scene key {scenekey}")
                    yield scenekey


def get_item_from_key(key):
    # Get metadata from JSON file on S3.
    logger.info(f"Getting object {key}")
    s3 = boto3.client("s3")
    item = s3.get_object(
        Bucket=const.LS8_L2_BUCKET_NAME,
        Key=key,
        RequestPayer="requester",
    )
    item = item["Body"].read()
    item = item.decode("utf-8")
    item = json.loads(item)
    # Make some quality control tests.
    if item["type"] != "Feature":
        raise ValueError(f"Item type must be Feature, found {item['type']}")

    if item["collection"] != const.LS8_L2_COLLECTION_ID:
        raise ValueError(
            f"Invalid collection for LS8 L2. Got {item['collection_id']}"
            " expected {const.LS8_L2_COLLECTION_ID}."
        )

    return Item(
        id=item["id"],
        stac_version=item["stac_version"],
        stac_extensions=item["stac_extensions"],
        geometry=json.dumps(item.pop("geometry")),
        bbox=item["bbox"],
        properties=item["properties"],
        assets=item["assets"],
        collection_id=item["collection"],
        parent_collection=item["parent_collection"],
        datetime=datetime.strptime(
            item["properties"]["datetime"], const.DATETIME_RFC339
        ),
        links=item["links"],
    )


def ingest_LS8_L2_bucket_items():
    # Ensure target collection exists.
    collection = session.query(Collection).get(const.LS8_L2_COLLECTION_ID)
    logger.info(f"Found collection {collection.id}")
    batch = []
    counter = 0
    logger.info("Registering items")
    for stac_key_base in get_ls8_l2_keys():
        stac_key = (
            stac_key_base + stac_key_base.split("/")[-2] + "_SR_stac.json"
        )
        counter += 1
        batch.append(stac_key)
        # Continue adding more item keys to batch until batch size is reached.
        if len(batch) < const.INGESTION_BATCH_SIZE:
            continue
        logger.info("Downloading item data for batch")
        # Get item data.
        with Pool(min(const.INGESTION_BATCH_SIZE, 10)) as pl:
            items = pl.map(get_item_from_key, batch)

        logger.info("Downloading item data for batch complete")
        # Save items to DB.
        logger.info("Commiting items", counter)
        session.bulk_save_objects(items)
        batch = []
        logger.info("Commiting items done")


def process_ls_sns_message(payload):
    # Temporary print to undestand what the payload looks like.
    print(payload)


ingest_LS8_L2_bucket_items()

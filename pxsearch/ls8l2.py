import json
from datetime import datetime
from multiprocessing import Pool

import boto3

from pxsearch import const, insert_ignore
from pxsearch.db import session
from pxsearch.models.stac import Collection, Item

DATETIME_RFC339 = "%Y-%m-%dT%H:%M:%S.%fZ"


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


def get_ls8_l2_keys():
    for year in range(2013, 2021):
        for lon in range(164, 171):
            for lat in range(67, 80):
                latkey = f"{const.LS8_L2_PAGINATOR_BASE_PREFIX}{year}/{str(lon).zfill(3)}/{str(lat).zfill(3)}/"
                # for yearkey in get_keys(const.LS8_L2_PAGINATOR_BASE_PREFIX):
                #     print(yearkey)
                #     for lonkey in get_keys(yearkey):
                #         print(lonkey)
                #         for latkey in get_keys(lonkey):
                # print(latkey)
                for scenekey in get_keys(latkey):
                    yield scenekey


def get_ls8_l2_iterator():
    client = boto3.client(const.CLIENT_TYPE)
    paginator = client.get_paginator(const.PAGINATOR_LOOKUP)
    prefix = const.LS8_L2_PAGINATOR_BASE_PREFIX
    iterator = paginator.paginate(
        Bucket=const.LS8_L2_BUCKET_NAME,
        Prefix=prefix,
        RequestPayer="requester",
        PaginationConfig={"PageSize": 10000},
    )
    return iterator


def get_item_from_key(key):
    s3 = boto3.client("s3")
    item = s3.get_object(
        Bucket=const.LS8_L2_BUCKET_NAME,
        Key=key,
        RequestPayer="requester",
    )
    item = item["Body"].read()
    item = item.decode("utf-8")
    item = json.loads(item)
    item["collection_id"] = item.pop("collection")
    item["geometry"] = json.dumps(item.pop("geometry"))
    item["datetime"] = datetime.strptime(
        item["properties"]["datetime"], DATETIME_RFC339
    )
    item.pop("description")
    # Ensure type is Feature.
    item_type = item.pop("type")
    if item_type != "Feature":
        raise ValueError(f"Item type must be Feature, found {item_type}")
    return Item(**item)


def ingest_LS8_L2_bucket_items():
    # Ensure target collection exists.
    collection = session.query(Collection).get(const.LS8_L2_COLLECTION_ID)
    print("Found collection", collection.id)

    batch = []
    counter = 0
    print("Getting iterator")
    iterator = get_ls8_l2_iterator()
    print("Registering items")
    for stac_key_base in get_ls8_l2_keys():
        print("stac_key_base", stac_key_base)
        stac_key = stac_key_base + stac_key_base.split("/")[-2] + "_SR_stac.json"
        counter += 1
        batch.append(stac_key)
        print("counting", counter)
        if len(batch) == const.INGESTION_BATCH_SIZE:
            print("Downloading batch")
            # Get item data.
            with Pool(min(const.INGESTION_BATCH_SIZE, 10)) as pl:
                items = pl.map(get_item_from_key, batch)
            print("Downloading batch complete")
            # Add to session and commit.
            for item in items:
                session.add(item)
            print("Commiting items", counter)
            session.commit()
            batch = []
            print("Commiting items done")

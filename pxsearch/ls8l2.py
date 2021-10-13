import json
from multiprocessing import Pool

import boto3
from sqlalchemy.orm import sessionmaker

from pxsearch import const
from pxsearch.db import engine
from pxsearch.models.stac import Collection, Item


def get_db_session():
    Session = sessionmaker(bind=engine)
    return Session()


def get_ls8_l2_iterator():
    client = boto3.client(const.CLIENT_TYPE)
    paginator = client.get_paginator(const.PAGINATOR_LOOKUP)
    prefix = const.LS8_L2_PAGINATOR_BASE_PREFIX
    iterator = paginator.paginate(
        Bucket=const.LS8_L2_BUCKET_NAME, Prefix=prefix, RequestPayer="requester"
    )
    return iterator.search(const.LS8_L2_STAC_ITEM_FILE_JMES_SEARCH)


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
    return Item(**item)


def ingest_LS8_L2_bucket_items():

    session = get_db_session()

    # Ensure target collection exists.
    collection = session.query(Collection).get(const.LS8_L2_COLLECTION_ID)
    print("Found collection", collection.id)

    batch = []
    for index, stac_key in enumerate(get_ls8_l2_iterator()):
        print(stac_key)
        batch.append(stac_key)
        if len(batch) == const.INGESTION_BATCH_SIZE:
            # Get item data.
            with Pool(const.INGESTION_BATCH_SIZE) as pl:
                items = pl.map(get_item_from_key, batch)
            # Add to session and commit.
            for item in items:
                session.add(item)
            print("Commiting items", index)
            session.commit()
            batch = []

import json
from typing import Collection

import boto3
import requests
from dateutil import parser
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from pxsearch.models.stac import Collection as CollectionModel
from pxsearch.models.stac import Item


def is_last_page(data: dict) -> bool:
    """
    Determine if a response is the last page of a STAC search
    """
    links = data.get("links")
    if not links:
        return True
    next_link = [dat for dat in links if dat.get("rel") == "next"]
    if not next_link:
        return True
    return False


def ensure_trailing_slash(url: str) -> str:
    if not url.endswith("/"):
        url += "/"
    return url


def get_requests_retry_session(
    retries: int = 3,
    backoff_factor: float = 0.3,
    status_forcelist: Collection[int] = (500, 502, 503, 504),
) -> requests.Session:
    """
    Get a session with retry policy set up.
    """
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def instantiate_items(
    data: Collection[dict],
) -> Collection[Item]:
    items = []
    for item in data:

        geometry = item.get("geometry")
        if geometry is not None:
            geometry = json.dumps(geometry)

        items.append(
            Item(
                id=item["id"],
                stac_version=item["stac_version"],
                stac_extensions=item["stac_extensions"],
                geometry=geometry,
                bbox=item.get("bbox"),
                properties=item["properties"],
                assets=item["assets"],
                collection_id=item["collection"],
                parent_collection=item.get("parent_collection", None),
                datetime=parser.parse(item["properties"]["datetime"]),
                links=item["links"],
            )
        )
    return items


def instantiate_collections(
    data: Collection[dict],
) -> Collection[Collection]:
    collections = []
    for collection in data:
        collections.append(
            CollectionModel(
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
                type=collection.get("type", "Collection"),
            )
        )
    return collections


def open_usgs_landsat_file(key):
    s3 = boto3.client("s3")
    item_raw = s3.get_object(
        Bucket="usgs-landsat", Key=key, RequestPayer="requester"
    )["Body"]
    return item_raw

import datetime
from typing import Optional
from urllib.parse import urljoin

import structlog
from requests.exceptions import JSONDecodeError

from pxsearch.db import session
from pxsearch.db_fixtures import pg_on_conflict_do_nothing  # noqa: F401
from pxsearch.ingest.const import INGEST_CHUNK_SIZE, MAX_DECODE_ERROR_ATTEMPTS
from pxsearch.ingest.utils import (
    create_ingest_intervals,
    ensure_trailing_slash,
    get_requests_retry_session,
    instantiate_collections,
    instantiate_items,
    is_last_page,
)

logger = structlog.get_logger(__name__)


def ingest_stac_interval(
    stac_url: str,
    interval: str,
    limit_collections: Optional[list] = None,
    split_day: Optional[int] = None,
    attempt: int = 0,
) -> None:
    """
    Ingest all STAC items for a time interval
    """
    # Build search url
    stac_search_url = urljoin(ensure_trailing_slash(stac_url), "search")
    logger.debug(f"STAC search url is {stac_search_url}")
    # Get data from all available pages of search result
    page = 1
    features = []
    requests_session = get_requests_retry_session()
    while True:
        params = {
            "datetime": interval,
            "limit": 250,
            "page": page,
        }
        if limit_collections:
            params["collections"] = limit_collections

        response = requests_session.post(
            stac_search_url,
            json=params,
        )
        # Sometimes stac APIs return corrupted json data.
        try:
            data = response.json()
        except JSONDecodeError:
            if attempt < MAX_DECODE_ERROR_ATTEMPTS:
                logger.info(
                    f"Caught JSONDecodeError at {stac_url}"
                    f" for interval {interval} and attempt {attempt}"
                )
                ingest_stac_interval(
                    stac_url=stac_url,
                    interval=interval,
                    limit_collections=limit_collections,
                    split_day=split_day,
                    attempt=attempt + 1,
                )
            else:
                logger.warning(
                    "Caught last JSONDecodeError and skip over"
                    " Will commit collected items and return"
                )
                break
        features += data["features"]
        page += 1
        if is_last_page(data):
            break

    items = instantiate_items(features)

    logger.info(f"Interval {interval} | commiting {len(items)} items to DB")
    for i in range(0, len(items), INGEST_CHUNK_SIZE):
        chunk = items[i : i + INGEST_CHUNK_SIZE]  # noqa: E203
        session.bulk_save_objects(chunk)
        session.commit()


def ingest_stac_year(
    stac_url: str,
    year: int,
    already_done: Optional[datetime.datetime] = None,
    split_day: Optional[int] = None,
    limit_collections: Optional[list] = None,
) -> None:
    """
    Ingest all STAC items for a year
    """
    intervals = create_ingest_intervals(
        year=year, already_done=already_done, split_day=split_day
    )
    logger.info(
        f"Starting ingestion of {len(intervals)} "
        f"{'day splits' if split_day else 'days'} "
        f"of data for year {year}"
    )
    for interval in intervals:
        ingest_stac_interval(stac_url, interval, limit_collections, split_day)
    logger.info(f"Finished processing all data for year {year}")


def ingest_stac_collections(stac_url: str) -> None:
    """
    Ingest all STAC collections
    """
    stac_collections_url = urljoin(
        ensure_trailing_slash(stac_url), "collections"
    )
    logger.debug(f"STAC collections url is {stac_collections_url}")
    # Get list of collections stored in the STAC api
    data = get_requests_retry_session().get(stac_collections_url).json()

    collections = instantiate_collections(data["collections"])

    logger.info(f"Saving {len(collections)} collections")
    session.bulk_save_objects(collections)
    session.commit()

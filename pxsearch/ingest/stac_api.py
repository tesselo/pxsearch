import datetime
import logging
from urllib.parse import urljoin

from requests.exceptions import JSONDecodeError

from pxsearch.db import session
from pxsearch.db_fixtures import pg_on_conflict_do_nothing  # noqa: F401
from pxsearch.ingest.utils import (
    ensure_trailing_slash,
    get_requests_retry_session,
    instantiate_collections,
    instantiate_items,
    is_last_page,
)

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

INGEST_CHUNK_SIZE = 500
MAX_JSON_DECODE_ERROR_ATTEMPTS = 3


def ingest_stac_day(
    stac_url: str, day: datetime.date, attempt: int = 0
) -> None:
    """
    Ingest all STAC items for a single day
    """
    # Build search url
    stac_search_url = urljoin(ensure_trailing_slash(stac_url), "search")
    logger.debug(f"STAC search url is {stac_search_url}")
    # Get data from all available pages of search result
    page = 1
    features = []
    requests_session = get_requests_retry_session()
    while True:
        response = requests_session.get(
            stac_search_url,
            params={
                "datetime": str(day),
                "limit": 250,
                "page": page,
            },
        )
        # Sometimes stac APIs return corrupted json data.
        try:
            data = response.json()
        except JSONDecodeError:
            if attempt < MAX_JSON_DECODE_ERROR_ATTEMPTS:
                logger.info(
                    "Caught JSONDecodeError at {stac_url}"
                    " for day {day} and attempt {attempt}"
                )
                ingest_stac_day(stac_url, day, attempt + 1)
            else:
                raise

        features += data["features"]
        page += 1
        if is_last_page(data):
            break

    items = instantiate_items(features)

    logger.info(f"Day {day} | commiting {len(items)} items to DB")
    for i in range(0, len(items), INGEST_CHUNK_SIZE):
        chunk = items[i : i + INGEST_CHUNK_SIZE]  # noqa: E203
        session.bulk_save_objects(chunk)
        session.commit()


def ingest_stac_year(
    stac_url: str, year: int, already_done: datetime.date = None
) -> None:
    """
    Ingest all STAC items for a year
    """
    date = datetime.date(year, 1, 1)
    already_done = already_done or date
    days = []
    while date <= datetime.date(year, 12, 31):
        if date >= already_done:
            days.append(date)
        date = date + datetime.timedelta(days=1)
    logger.info(
        f"Starting ingestion of {len(days)} days of data for year {year}"
    )
    for day in days:
        ingest_stac_day(stac_url, day)
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

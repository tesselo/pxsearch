import datetime

from pxsearch.db import session
from pxsearch.ingest.stac_api import (
    ingest_stac_collections,
    ingest_stac_interval,
    ingest_stac_year,
)
from pxsearch.models.stac import Collection, Item
from tests.conftest import STAC_TEST_URL, setup_stac_requests_mock


def test_ingest_stac_collections(requests_mock):
    item, collection = setup_stac_requests_mock(requests_mock)
    ingest_stac_collections(STAC_TEST_URL)
    db_result = session.query(Collection).all()
    assert db_result[0].id == collection["id"]


def test_ingest_stac_interval(requests_mock):
    item, collection = setup_stac_requests_mock(requests_mock)
    ingest_stac_collections(STAC_TEST_URL)
    ingest_stac_interval(
        STAC_TEST_URL, str(datetime.datetime.now().date()), split_day=2
    )
    db_result = session.query(Item).all()
    assert db_result[0].id == item["id"]


def test_ingest_stac_year(requests_mock):
    item, collection = setup_stac_requests_mock(requests_mock)
    ingest_stac_collections(STAC_TEST_URL)
    ingest_stac_year(STAC_TEST_URL, 1972)
    db_result = session.query(Item).all()
    assert db_result[0].id == item["id"]

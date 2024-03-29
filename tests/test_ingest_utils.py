import datetime
import json

from pxsearch.ingest.utils import (
    create_ingest_intervals,
    ensure_trailing_slash,
    get_requests_retry_session,
    instantiate_collections,
    instantiate_items,
    is_last_page,
)


def test_is_last_page_empty():
    assert is_last_page({})


def test_is_last_page_no_next_link():
    assert is_last_page({"links": [{"rel": "notnext"}]})


def test_is_not_last_page():
    assert is_last_page({"links": [{"rel": "next"}]}) is False


def test_ensure_trailing_slash_add():
    assert ensure_trailing_slash("https://example.com/stac/v0").endswith("/")


def test_ensure_trailing_slash_already_there():
    assert ensure_trailing_slash("https://example.com/stac/v0/").endswith("/")


def test_get_requests_retry_session():
    sess = get_requests_retry_session(
        retries=4, backoff_factor=0.23, status_forcelist=(404,)
    )
    retry = sess.adapters.pop("https://").max_retries
    assert retry.total == 4
    assert retry.backoff_factor == 0.23
    assert retry.status_forcelist == (404,)


def test_convert_item_data_to_item_objects():
    with open("tests/data/test_item.json") as src:
        item = json.load(src)
    items = instantiate_items([item, item])
    assert len(items) == 2
    assert items[0].id == "test-item"


def test_load_collection(test_db_session):
    with open("tests/data/test_collection.json") as src:
        collection = json.load(src)
    collections = instantiate_collections([collection, collection])
    assert len(collections) == 2
    assert collections[0].id == "test-collection"


def test_create_ingest_intervals():
    result = create_ingest_intervals(
        2020, already_done=datetime.datetime(2020, 12, 29), split_day=3
    )
    expected = [
        "2020-12-29T00:00:00Z/2020-12-29T08:00:00Z",
        "2020-12-29T08:00:00Z/2020-12-29T16:00:00Z",
        "2020-12-29T16:00:00Z/2020-12-30T00:00:00Z",
        "2020-12-30T00:00:00Z/2020-12-30T08:00:00Z",
        "2020-12-30T08:00:00Z/2020-12-30T16:00:00Z",
        "2020-12-30T16:00:00Z/2020-12-31T00:00:00Z",
        "2020-12-31T00:00:00Z/2020-12-31T08:00:00Z",
        "2020-12-31T08:00:00Z/2020-12-31T16:00:00Z",
        "2020-12-31T16:00:00Z/2021-01-01T00:00:00Z",
    ]
    assert result == expected

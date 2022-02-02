import json

import pytest
from sqlalchemy import create_engine

from pxsearch.utils import get_connection_url

STAC_TEST_URL = "https://example.com/stac/v0"


@pytest.fixture(scope="session")
def database_engine():
    engine = create_engine(get_connection_url())
    yield engine
    engine.execute("DROP SCHEMA data CASCADE")
    engine.execute("DROP EXTENSION IF EXISTS postgis")


def setup_stac_requests_mock(requests_mock):
    with open("tests/data/test_item.json") as src:
        item = json.load(src)
    requests_mock.get(STAC_TEST_URL + "/search", json={"features": [item]})

    with open("tests/data/test_collection.json") as src:
        collection = json.load(src)
    requests_mock.get(
        STAC_TEST_URL + "/collections", json={"collections": [collection]}
    )

    return item, collection

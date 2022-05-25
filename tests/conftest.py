import json

import pytest
from sqlalchemy import create_engine, inspect

from pxsearch.db import session
from pxsearch.utils import get_connection_url

STAC_TEST_URL = "https://example.com/stac/v0"


@pytest.fixture(scope="session", autouse=True)
def database_engine():
    connection_url = get_connection_url()
    if "localhost" not in connection_url:
        raise ValueError("Avoiding to run tests in non local database")
    engine = create_engine(connection_url)
    yield engine
    engine.execute("DROP SCHEMA data CASCADE")
    engine.execute("DROP EXTENSION IF EXISTS postgis")


@pytest.fixture(autouse=True)
def exploding_session(database_engine):
    yield session
    session.rollback()
    for table in inspect(database_engine).get_table_names(schema="data"):
        session.execute(f"TRUNCATE TABLE data.{table} CASCADE")
    session.commit()


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

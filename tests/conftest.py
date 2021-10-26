import pytest
from sqlalchemy import create_engine

from pxsearch.utils import get_connection_url


@pytest.fixture(scope="session")
def database_engine():
    engine = create_engine(get_connection_url("pxsearch_test"))
    yield engine
    engine.execute("DROP SCHEMA data CASCADE")
    engine.execute("DROP EXTENSION IF EXISTS postgis")

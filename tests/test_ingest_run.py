from click.testing import CliRunner

from pxsearch.ingest.run import ingest_year_range
from pxsearch.models.stac import Collection, Item
from tests.conftest import STAC_TEST_URL, setup_stac_requests_mock


def test_ingest_run(requests_mock, test_db_session):
    item, collection = setup_stac_requests_mock(requests_mock)
    runner = CliRunner()
    # Run ingest collection list
    runner.invoke(
        ingest_year_range, f"--stac-url={STAC_TEST_URL} --ingest-collections"
    )
    db_result = test_db_session.query(Collection).all()
    assert db_result[0].id == collection["id"]
    # Run ingest year
    runner.invoke(
        ingest_year_range, f"--stac-url={STAC_TEST_URL} --year-start=1972"
    )
    db_result = test_db_session.query(Item).all()
    assert db_result[0].id == item["id"]

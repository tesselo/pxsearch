import json
from unittest.mock import MagicMock, patch

from pxsearch.db import session
from pxsearch.ingest.signals import ingest_s2_signal, ingest_usgs_signal
from pxsearch.ingest.utils import instantiate_collections
from pxsearch.models.stac import Item

item_data_mock = MagicMock(
    return_value=open("tests/data/test_item.json", "rb")
)

item_list_mock = MagicMock(return_value=["path/to/some/stacitem_stac.json"])


def setup_collections():
    """
    Register collection before registering item.
    """
    with open("tests/data/test_collection.json") as src:
        collection = json.load(src)
    collections = instantiate_collections([collection])
    session.bulk_save_objects(collections)
    session.commit()


@patch(
    "pxsearch.ingest.signals.list_usgs_landsat_stac_prefixes", item_list_mock
)
@patch("pxsearch.ingest.signals.open_usgs_landsat_file", item_data_mock)
def test_ingest_item_from_signal():
    setup_collections()
    with open("tests/data/test_signal_usgs.json") as src:
        event = json.load(src)
    ingest_usgs_signal(event)
    db_result = session.query(Item).all()
    assert len(db_result) == 1


def test_ingest_item_from_s2_signal():
    setup_collections()
    with open("tests/data/test_signal_s2.json") as src:
        event = json.load(src)
    ingest_s2_signal(event)
    db_result = session.query(Item).all()
    assert len(db_result) == 1

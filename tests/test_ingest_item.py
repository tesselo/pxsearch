import json

from pxsearch.models.stac import Collection


def test_load_collection(test_db_session):
    with open("tests/data/test_collection.json") as src:
        data = json.load(src)
    collection = Collection(**data)
    test_db_session.add(collection)
    test_db_session.commit()
    expected = [collection]
    result = test_db_session.query(Collection).all()
    assert result == expected

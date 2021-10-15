#Aproach with sql alchemy
import json, sys
# import the psycopg2 database adapter for PostgreSQL
from psycopg2 import connect, Error
from pxsearch.models.stac import Collection, Item
from pxsearch.utils import get_connection_url
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


# Open the data file
items_file="/home/keren/Repositories/pxsearch/tests/data/test_item.json"


def ingest_data(source_file):
    #Data to ingest
    source_file = source_file
    #Open data
    with open(source_file) as source_file:
        data_dict= json.load(source_file)
    # Connect to db
    engine = create_engine(get_connection_url())
    # Add data to the table items
    with Session(engine) as session:
        if data_dict.get("type") == "Collection":
            data = Collection(**data_dict)
        else:
            data_dict["geometry"] = json.dumps(data_dict.pop("geometry"))
            data_dict.pop("type")
            data_dict.pop("collection")
            data = Item(**data_dict)
          
        session.add(data)
        session.commit()

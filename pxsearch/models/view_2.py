from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.sql import select
from sqlalchemy_views import CreateView, DropView
from pxsearch.utils import get_connection_url
from sqlalchemy import create_engine

# Connect to db
engine = create_engine(get_connection_url())

#Metadata
metadata = MetaData()

# Load Tables
items = Table("items", metadata, autoload=True, autoload_with=engine, schema="data")
collections = Table("collections", metadata, autoload=True, autoload_with=engine, schema="data")


#View
view = Table('my_view', metadata, schema="data")

#  JSONB datatype should be used explicitly.
# https://docs.sqlalchemy.org/en/14/dialects/postgresql.html#sqlalchemy.dialects.postgresql.JSON
# https://newbedev.com/python-sqlalchemy-and-postgres-how-to-query-a-json-element
definition = select([
    items.c.collection_id,
    items.c.id.label('product_id'),
    items.c.datetime.label('sensing_time'), 
    #items.c.links["rel"].astext == "self".label('base_url'),
    items.c.properties["platform"].label("spacecraft_id"),
    items.c.properties["instruments"].label("sensor_id"),
    items.c.properties["proj:transform"].label("bbox"),
    items.c.properties["landsat:wrs_row"].label("wrs_row"),
    items.c.properties["landsat:wrs_path"].label("wrs_path"),
    items.c.properties["landsat:cloud_cover_land"].label("cloud_cover")]
    ).where(collections.c.id == items.c.collection_id) 

create_view = CreateView(view, definition, or_replace=True)
print(str(create_view.compile()).strip())
#In pgadmin:ERROR:  cannot subscript type jsonb because it is not an array SQL state: 42804


# reflect view and print result
v = Table('my_view', metadata, autoload=True,autoload_with=engine)
for row in engine.execute(v.select()):   #NOT WORKING YET
    print(row)


#Drop view
drop_view = DropView(view, if_exists=True, cascade=True)


# To get all info about db  
metadata.reflect(engine) 
# To get tables names
metadata.tables.keys()
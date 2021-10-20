from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.sql import select
from sqlalchemy_views import CreateView, DropView
from pxsearch.utils import get_connection_url
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSON, JSONB
from sqlalchemy.sql.expression import cast
from sqlalchemy import *
import json 
#import iso8601

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
# https://sqlalchemy.narkive.com/oIndXuqi/sqlalchemy-core-jsonb-in-dynamic-select

definition = select([
    items.c.collection_id,
    items.c.id.label('product_id'),
    items.c.datetime.label('sensing_time'), 
    items.c.links["rel"].astext == "self".label('base_url'),
    items.c.properties["platform"].label("spacecraft_id"),
    items.c.properties["instruments"].label("sensor_id"),
    cast(str(items.c.properties["proj:transform"]), JSONB).label("bbox"),
    items.c.properties["landsat:wrs_row"].label("wrs_row"),
    items.c.properties["landsat:wrs_path"].label("wrs_path"),
    items.c.properties["landsat:cloud_cover_land"].label("cloud_cover")]
]).where(collections.c.id == items.c.collection_id) 

#engine.execute(definition)
#print(engine.execute(definition).first())

create_view = CreateView(view, definition, or_replace=True)
print(str(create_view.compile()).strip())
#It is not creating the view, Checking in pgadmin I had an ERROR:  cannot subscript type jsonb because it is not an array SQL state: 42804

# Reflect view and print result
v = Table('my_view', metadata, autoload=True,autoload_with=engine)
for row in engine.execute(v.select()):   #NOT WORKING YET
    print(row)

#Drop view
drop_view = DropView(view, if_exists=True, cascade=True)

# To get all info about db  
metadata.reflect(engine) 
# To get tables names
metadata.tables.keys()

#############################################################################################################
# TESTS
# Trying to access jsonb keys for links:
relations = select([
func.jsonb_array_elements(
literal(["rel", "href"], JSONB),
type_=String
).label('test')
]).alias('relations')

test = select([
    items.c.links
]).limit(1)
result = engine.execute(test).fetchall()

for r in result:
    json_result = r['links']
    # print(type(json_result))
    print("# json_result: ", json_result)
    filtered = filter(lambda json_obj: json_obj['rel'] == "self", json_result)
    print("# Filtered: ", list(filtered))
    for json_obj in json_result:
        if json_obj['rel'] == 'self':
            print(json_obj['href'])



stmt = select([
func.string_agg(
cast(relations.c.test, JSONB)[()].astext,
" , "
)
])

print(engine.execute(stmt).fetchall())

links = select([
func.jsonb_a(
literal(["rel", "href"], JSONB),
type_=String
).label('test')
]).alias('relations')

for row in engine.execute(relations.select()):   #NOT WORKING YET
    print(row)
##################################################


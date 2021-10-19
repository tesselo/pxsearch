import os
from sqlalchemy import Table
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import Executable, ClauseElement
from pxsearch.utils import get_connection_url
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import select, func

class CreateView(Executable, ClauseElement): 
    def __init__(self, name, select):
        self.name = name
        self.select = select

@compiles(CreateView)
def visit_create_view(element, compiler, **kw): 
    return "CREATE VIEW %s AS %s" % (
         element.name,
         compiler.process(element.select, literal_binds=True)
         )

# test data
from sqlalchemy import MetaData, Column, Integer

# Connect to db
engine = create_engine(get_connection_url())

# Instatiation of Metadata - a container object that keeps together many different features of a database (or multiple databases) being described.
metadata = MetaData(engine) 
# To get all info about db  
metadata.reflect(engine) 
# To get tables names
metadata.tables.keys()

# Load Tables
items = Table("items", metadata, autoload=True, autoload_with=engine, schema="data")
collections = Table("collections", metadata, autoload=True, autoload_with=engine, schema="data")

#Define view columns
definition = select([
    items.c.collection_id,
    items.c.id.label('product_id'),
    items.c.datetime.label('sensing_time'), 
    items.c.links["rel"].astext == "self".label('base_url'),
    items.c.properties["platform"].label("spacecraft_id"),
    items.c.properties["instruments"].label("sensor_id"),
    items.c.properties["proj:transform"].label("bbox"),
    items.c.properties["landsat:wrs_row"].label("wrs_row"),
    items.c.properties["landsat:wrs_path"].label("wrs_path"),
    items.c.properties["landsat:cloud_cover_land"].label("cloud_cover")]
    ).where(collections.c.id == items.c.collection_id)  # Não sei se isso vai funcionar!!!!!


# preciso chamar id? Não será usado pela search mas pode ser necessário para o inner join?
# preciso converter sensing time  para mesmo formato da imagery?
# preciso fazer um string format no sensor id?

# create view
createview = CreateView('imagery', definition)
engine.execute(createview)

# reflect view and print result
v = Table('imagery', metadata, autoload=True)
for r in engine.execute(v.select()):
    print(r)
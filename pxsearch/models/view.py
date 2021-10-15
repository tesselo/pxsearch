import os
from sqlalchemy import Table
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import Executable, ClauseElement
from pxsearch.utils import get_connection_url
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

class CreateView(Executable, ClauseElement): # O que isso faz?
    def __init__(self, name, select):
        self.name = name
        self.select = select

@compiles(CreateView)
def visit_create_view(element, compiler, **kw):  # O que isso faz?
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

#Colunas necessarias para search:   
    # geojson,
    # start=None,
    # end=None,
    # platforms=None,
    # maxcloud=None,
    # scene=None,
    # sensor=None,
    # level=None,
    # limit=10,
    # sort="sensing_time"

# How to instantiate table imagery?
table = "items"

definition = select([
    table.id.label('table_b_id'),
    table.coupon_code,
    table.number_of_rebought_items,
]).select_from(table.__table__.outerjoin(TableA, table.generate_action == TableA.id))


# create view
createview = CreateView('imagery', definition)
engine.execute(createview)

# reflect view and print result
v = Table('viewname', metadata, autoload=True)
for r in engine.execute(v.select()):
    print(r)
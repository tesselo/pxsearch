# VIEW is a query stored in the db. 
# We can use/query a VIEW as a table. ~ virtual table
# Based on: https://newbedev.com/how-to-create-an-sql-view-with-sqlalchemy
# More references: https://docs.sqlalchemy.org/en/14/core/metadata.html

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

# To represent a table, use the Table class. 
# Its two primary arguments are the table name, then the MetaData object which it will be associated with. 
# The remaining positional arguments are mostly Column objects describing each column:
t = Table('t',
          metadata,
          Column('id', Integer, primary_key=True),
          Column('number', Integer))
t.create()
engine.execute(t.insert().values(id=1, number=3))
engine.execute(t.insert().values(id=9, number=-3))

# create view
createview = CreateView('viewname', t.select().where(t.c.id>5))
engine.execute(createview)

# reflect view and print result
v = Table('viewname', metadata, autoload=True)
for r in engine.execute(v.select()):
    print(r)
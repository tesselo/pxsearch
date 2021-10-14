# VIEW is a query stored in the db. 
# We can use/query a VIEW as a table. ~ virtual table
# Based on: https://newbedev.com/how-to-create-an-sql-view-with-sqlalchemy
import os
from sqlalchemy import Table
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import Executable, ClauseElement
#from pxsearch.utils import get_connection_url
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

import os

def get_connection_url() -> str:
    """
    Get connection URL from environment variables
    (see environment variables set in docker-compose)
    """
    postgres_user = os.environ["POSTGRES_USER"]
    postgres_pass = os.environ["POSTGRES_PASS"]
    postgres_host = os.environ["POSTGRES_HOST"]
    postgres_port = os.environ.get("POSTGRES_PORT", "5432")
    postgres_dbname = os.environ["POSTGRES_DBNAME"]
    return f"postgresql://{postgres_user}:{postgres_pass}@{postgres_host}:{postgres_port}/{postgres_dbname}"

export DB_NAME='pixels'
export DB_PASSWORD='postgres'
export DB_HOST='localhost'
export DB_USER='postgres

# test data
from sqlalchemy import MetaData, Column, Integer
from sqlalchemy.engine import create_engine
# Connect to db
engine = create_engine(get_connection_url())
metadata = MetaData(engine)
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
    print r
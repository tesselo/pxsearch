import os

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker

user = os.environ.get("USER", "postgres")
pw = os.environ.get("PASS", "")
host = os.environ.get("HOST", "localhost")
port = os.environ.get("PORT", "5432")
dbname = os.environ.get("DBNAME", "pxsearch_test")
url = f"postgresql://{user}:{pw}@{host}:{port}/{dbname}"

metadata = MetaData()
engine = create_engine(url)
session = sessionmaker(engine)()

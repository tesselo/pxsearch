from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker

from pxsearch.utils import get_connection_url

metadata = MetaData()
engine = create_engine(get_connection_url(), pool_pre_ping=True)
session = sessionmaker(bind=engine)()

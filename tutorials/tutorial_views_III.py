#Reference: https://newbedev.com/how-to-create-an-sql-view-with-sqlalchemy
#https://pypi.org/project/sqlalchemy-views/
#From it's PyPI Page:

# from sqlalchemy import Table, MetaData
# from sqlalchemy.sql import text
# from sqlalchemy_views import CreateView, DropView

# view = Table('my_view', metadata)
# definition = text("SELECT * FROM my_table")

# create_view = CreateView(view, definition, or_replace=True)
# print(str(create_view.compile()).strip())
# CREATE OR REPLACE VIEW my_view AS SELECT * FROM my_table

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.sql import select
from sqlalchemy_views import CreateView, DropView


#Metadata
metadata = MetaData()


#Tables
users = Table('users', metadata,
      Column('id', Integer, primary_key=True),
      Column('name', String),
      Column('fullname', String),
  )

addresses = Table('addresses', metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', None, ForeignKey('users.id')),
    Column('email_address', String, nullable=False)
   )


#View
view = Table('my_view', metadata)
definition = select([users, addresses]).where(
    users.c.id == addresses.c.user_id
)

create_view = CreateView(view, definition, or_replace=True)
print(str(create_view.compile()).strip())
#Output:
# CREATE OR REPLACE VIEW my_view AS SELECT users.id, users.name,
# users.fullname, addresses.id, addresses.user_id, addresses.email_address 
# FROM users, addresses 
# WHERE users.id = addresses.user_id

#Drop view
drop_view = DropView(view, if_exists=True, cascade=True)
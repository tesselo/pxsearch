import sqlalchemy_views
from sqlalchemy import Table
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.ddl import DropTable
from sqlalchemy import orm
from pxsearch.utils import get_connection_url
from sqlalchemy import create_engine

class View(Table):
    is_view = True


class CreateView(sqlalchemy_views.CreateView):
    def __init__(self, view):
        super().__init__(view.__view__, view.__definition__)


@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    if hasattr(element.element, 'is_view') and element.element.is_view:
        return compiler.visit_drop_view(element)

    # cascade seems necessary in case SQLA tries to drop 
    # the table a view depends on, before dropping the view
    return compiler.visit_drop_table(element) + ' CASCADE'

# Defining a view (e.g. globally like your Table models):

class SampleView:
    __view__ = View(
        'sample_view', MetaData(),
        Column('bar', Text, primary_key=True),
    )

    __definition__ = text('''select 'foo' as bar''')

# keeping track of your defined views makes things easier
views = [SampleView]

# Mapping the views (enable ORM functionality):
# Do when loading up your app, before any queries and after setting up the DB.

for view in views:
    if not hasattr(view, '_sa_class_manager'):
        orm.mapper(view, view.__view__)

#Creating the views:
#Do when initializing the database, e.g. after a create_all() call.

# Connect to db
engine = create_engine(get_connection_url())

for view in views:
    engine.execute(CreateView(view))

#How to query a view:

# results = engine.session.query(SomeModel, SampleView).join(
#     SampleView,
#     SomeModel.id == SampleView.some_model_id
# ).all()
# This would return exactly what you expect (a list of objects that each has a SomeModel object and a SampleView object).

#Dropping a view:

SampleView.__view__.drop(engine)
#It will also automatically get dropped during a drop_all() call.


#########################################
#Reference
#https://newbedev.com/how-to-create-an-sql-view-with-sqlalchemy

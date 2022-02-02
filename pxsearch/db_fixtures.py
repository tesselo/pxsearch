from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import Insert


@compiles(Insert, "postgresql")
def pg_on_conflict_do_nothing(insert, compiler, **kw):
    """
    Override insert statement to ignore duplicate primary key conflicts. This
    allows running this script against a database that already has some data
    populated.
    https://github.com/sqlalchemy/sqlalchemy/issues/5374#issuecomment-752693165
    """
    statement = compiler.visit_insert(insert, **kw)
    # IF we have a "RETURNING" clause, we must insert before it
    returning_position = statement.find("RETURNING")
    if returning_position >= 0:
        return (
            statement[:returning_position]
            + "ON CONFLICT DO NOTHING "
            + statement[returning_position:]
        )
    else:
        return statement + " ON CONFLICT DO NOTHING"

"""
When imported, automatically make all insert not fail on duplicate keys

Source: https://github.com/sqlalchemy/sqlalchemy/issues/5374#issuecomment-752693165
"""

from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import Insert


@compiles(Insert, "postgresql")
def postgresql_on_conflict_do_nothing(insert, compiler, **kw):
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

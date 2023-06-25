import sqlite3

from sqlalchemy                import event, exc
from sqlalchemy.engine         import Engine
from sqlalchemy.ext.compiler   import compiles
from sqlalchemy.sql.expression import func

from .expression import RegexMatchExpression, SQLITE_REGEX_FUNCTIONS



@event.listens_for(Engine, 'connect')
def sqlite_engine_connect(dbapi_connection, connection_record):
    if not isinstance(dbapi_connection, sqlite3.Connection):
        return

    for name, function in SQLITE_REGEX_FUNCTIONS.values():
        dbapi_connection.create_function(name, 2, function)



@compiles(RegexMatchExpression)
def sqlite_regex_match(element, compiler, **kw):
    operator = element.operator.opstring

    try:
        func_name, _ = SQLITE_REGEX_FUNCTIONS[operator]

    except (KeyError, ValueError) as e:
        would_be_sql_string = ' '.join((
            compiler.process(element.left),
            operator,
            compiler.process(element.right)
        ))

        raise exc.StatementError(
            'unknown regexp match operator: {}'.format(operator),
            would_be_sql_string,
            None,
            e
        )

    regex_fn      = getattr(func, func_name)
    regex_fn_call = regex_fn(element.left, element.right)
    return compiler.process(regex_fn_call)



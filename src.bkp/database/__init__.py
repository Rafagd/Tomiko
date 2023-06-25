from contextlib import contextmanager

from .event      import *
from .Author     import Author
from .Dictionary import Dictionary
from .Message    import Message
from .Slap       import Slap

@contextmanager
def scoped_session(Session):
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()



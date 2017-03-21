import enum

from contextlib                 import contextmanager
from sqlalchemy                 import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm             import relationship
from sqlalchemy.sql             import select, func
from telegram                   import Update

from .util import classproperty

Table = declarative_base()

class Author(Table):
    __tablename__ = 'authors'
    id         = Column(Integer, primary_key=True)
    first_name = Column(String,  nullable=False)
    last_name  = Column(String,  nullable=False)
    user_name  = Column(String,  nullable=False)

    def __repr__(self):
        name = self.user_name
        if name == '':
            name = '"{} {}"'.format(self.first_name, self.last_name)
        return '{}#{}'.format(name, self.id)


class Response(enum.Enum):
    NONE   = 0,
    RANDOM = 1


class Message(Table):
    __tablename__ = 'messages'
    id        = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('authors.id'))
    type      = Column(Integer, nullable=False)
    content   = Column(String,  nullable=False)
    mind      = Column(String,  nullable=False)
    why       = Response.NONE
    author    = relationship(Author)

    @classproperty
    def TYPE_COMMAND(self):
        return 0

    @classproperty
    def TYPE_TEXT(self):
        return 1

    @classproperty
    def TYPE_DOCUMENT(self):
        return 2

    @staticmethod
    def random(session):
        message     = session.query(Message).order_by(func.random()).limit(1).one()
        message.why = Response.RANDOM
        return message

    def __repr__(self):
        if self.type == Message.TYPE_TEXT:
            str_type = 'TXT'

        elif self.type == Message.TYPE_DOCUMENT:
            str_type = 'DOC'

        elif self.type == Message.TYPE_COMMAND:
            str_type = 'CMD'

        return '{}:"{}"'.format(str_type, self.content)


class Slap(Table):
    __tablename__ = 'slaps'
    id        = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('authors.id'))
    object    = Column(String,  nullable=False)


def create_all(engine):
    Table.metadata.create_all(engine)


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


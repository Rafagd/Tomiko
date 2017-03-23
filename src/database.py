import enum
import re

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

    @staticmethod
    def fetch(session, author_id):
        return session                      \
            .query(Author)                  \
            .filter(Author.id == author_id) \
            .limit(1)                       \
            .one()

    def __repr__(self):
        name = self.user_name
        if name == '':
            name = '"{} {}"'.format(self.first_name, self.last_name)
        return '{}#{}'.format(name, self.id)


class Message(Table):
    __tablename__ = 'messages'
    id        = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('authors.id'))
    type      = Column(Integer, nullable=False)
    content   = Column(String,  nullable=False)
    mind      = Column(String,  nullable=False)
    author    = relationship(Author)

    def TYPE_ERROR(self):
        return 0

    @classproperty
    def TYPE_COMMAND(self):
        return 1

    @classproperty
    def TYPE_TEXT(self):
        return 2

    @classproperty
    def TYPE_DOCUMENT(self):
        return 3

    @classproperty
    def TYPE_STICKER(self):
        return 4

    @staticmethod
    def fetch_random(session):
        return session               \
            .query(Message)          \
            .order_by(func.random()) \
            .limit(1)                \
            .one()

    @staticmethod
    def fetch_word(session, word=''):
        query = session                                \
            .query(Message)                            \
            .filter(Message.type == Message.TYPE_TEXT) \
            .order_by(func.random())                   \
            .limit(1)
        if word != '':
            try:
                return query.filter(
                    Message.content.contains(word) | 
                    Message.mind.contains(word)
                ).one()
            except:
                pass
        # If no word provided or nothing found, return random.
        return query.one()

    @staticmethod
    def fetch_document(session, word):
        query = session                                    \
            .query(Message)                                \
            .filter(Message.type == Message.TYPE_DOCUMENT) \
            .order_by(func.random())                       \
            .limit(1)
        if word != '':
            try:
                return query.filter(Message.mind.contains(word)).one()
            except:
                pass
        # If no word provided or nothing found, return random.
        return query.one()

    @staticmethod
    def fetch_sticker(session, word):
        query = session                                   \
            .query(Message)                               \
            .filter(Message.type == Message.TYPE_STICKER) \
            .order_by(func.random())                      \
            .limit(1)
        if word != '':
            try:
                return query.filter(Message.mind.contains(word)).one()
            except:
                pass
        # If no word provided or nothing found, return random.
        return query.one()

    def tokens(self):
        return re.split('\s+', self.content)

    def __repr__(self):
        if self.type == Message.TYPE_TEXT:
            str_type = 'TXT'

        elif self.type == Message.TYPE_DOCUMENT:
            str_type = 'DOC'

        elif self.type == Message.TYPE_COMMAND:
            str_type = 'CMD'

        elif self.type == Message.TYPE_STICKER:
            str_type = 'STK'

        return '{}:"{}"'.format(str_type, self.content)


class Slap(Table):
    __tablename__ = 'slaps'
    id        = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('authors.id'))
    object    = Column(String,  nullable=False)

    @staticmethod
    def fetch_random(session):
        return session               \
            .query(Slap)             \
            .order_by(func.random()) \
            .limit(1)                \
            .one()


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



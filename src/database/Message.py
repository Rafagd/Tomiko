import re

from sqlalchemy     import Column, ForeignKey, Integer, func
from sqlalchemy.orm import relationship

from .       import Author
from .common import DeclarativeBase
from .type   import String
from ..util  import classproperty


class Message(DeclarativeBase):
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
        msg     = query(session).one()
        msg.why = [ 'fetch_random' ]
        return msg


    @staticmethod
    def fetch_word(session, word=''):
        try:
            msg     = query(session, Message.TYPE_TEXT, word).one()
            msg.why = [ word, 'fetch_word' ]
        except:
            msg     = query(session, Message.TYPE_TEXT).one()
            msg.why = [ 'random_word', word, 'fetch_word' ]

        return msg


    @staticmethod
    def fetch_document(session, word):
        try:
            msg     = query(session, Message.TYPE_DOCUMENT, word).one()
            msg.why = [ word, 'fetch_document' ]
        except:
            msg      = query(session, Message.TYPE_DOCUMENT).one()
            msg.why += [ 'random_document', word, 'fetch_document' ]

        return msg


    @staticmethod
    def fetch_sticker(session, word):
        try:
            msg     = query(session, Message.TYPE_STICKER, word).one()
            msg.why = [ word, 'fetch_sticker' ]
        except:
            msg      = query(session, Message.TYPE_STICKER).one()
            msg.why += [ 'random_sticker', word, 'fetch_sticker' ]

        return msg


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



def query(session, msg_type=None, word='', limit=1):
    query = session.query(Message).order_by(func.random())

    if msg_type != None:
        query = query.filter(Message.type == msg_type)

    if word != '':
        query = query.filter(
            Message.content.contains(word) | Message.mind.contains(word)
        )

    if isinstance(limit, int):
        query = query.limit(limit)

    return query



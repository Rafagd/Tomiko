from sqlalchemy     import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .       import Author
from .common import DeclarativeBase
from .type   import String


class Slap(DeclarativeBase):
    __tablename__ = 'slaps'
    id        = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('authors.id'))
    object    = Column(String,  nullable=False)
    author    = relationship(Author)

    @staticmethod
    def fetch_random(session):
        return session               \
            .query(Slap)             \
            .order_by(func.random()) \
            .limit(1)                \
            .one()



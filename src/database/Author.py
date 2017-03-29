from sqlalchemy import Column, ForeignKey, Integer

from .common import DeclarativeBase
from .type   import String

class Author(DeclarativeBase):
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

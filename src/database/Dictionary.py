import re

from sqlalchemy import Column, Float, Integer

from .Message import Message
from .common  import DeclarativeBase
from .type    import String


class Dictionary(DeclarativeBase):
    __tablename__ = 'dictionary'
    id    = Column(Integer, primary_key=True)
    word  = Column(String,  nullable=False)
    score = Column(Float,   nullable=False)


    @staticmethod
    def fetch_scores(session, words):
        return session.query(Dictionary)                                    \
            .filter(Dictionary.word.iregexp('(' + ('|'.join(words)) + ')')) \
            .order_by(Dictionary.score.desc())                              \
            .all()


    @staticmethod
    def update(session):
        messages   = session.query(Message)
        dictionary = dict()
        max_repeat = 0

        for message in messages:
            for word in re.split('\W+', message.content + ' ' + message.mind):
                if word == '':
                    continue

                word = word.upper()

                try:
                    dictionary[word] += 1
                except:
                    dictionary[word] = 1

                if dictionary[word] > max_repeat:
                    # + 1 because I don't want zeroes in the DB.
                    max_repeat = dictionary[word] + 1
        
        session.query(Dictionary).delete()

        for word in dictionary:
            instance       = Dictionary()
            instance.word  = word
            instance.score = 1 - (dictionary[word] / max_repeat)
            session.add(instance)



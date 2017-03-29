import os
import random
import re

from sqlalchemy     import create_engine
from sqlalchemy.orm import sessionmaker
from telegram.ext   import Updater

from .telegram import *
from .database import *
from .command  import command
from .util     import ttl_set


class Main:
    def __init__(self, config):
        self.config   = config
        self.Session  = sessionmaker(bind=create_engine('sqlite:///data/database.sqlite'))
        self.updater  = Updater(token=config.token)
        self.metadata = self.updater.bot.get_me()
        self.handler  = UpdateHandler(self.metadata, self.message)
        self.mind     = ttl_set()

        self.updater.dispatcher.add_handler(self.handler)
        self.updater.dispatcher.add_error_handler(self.handler.error_handler)


    def message(self, api, update, error = None):
        with scoped_session(self.Session) as session:
            author     = read_author(update, session)
            message    = read_message(update, error)
            response   = None
            with_quote = False

            if message.type == Message.TYPE_ERROR:
                response = self.message_error(session, author, message)

            elif message.type == Message.TYPE_COMMAND:
                response = command(self, session, author, message)

            else:
                self.internalize(message)
                message.mind = str(self.mind)

                if self.memorizable(message):
                    session.add(message)

                self.mind.tick()

                mentions_me = re.search(
                    self.metadata.first_name,
                    message.content,
                    re.IGNORECASE
                )

                if mentions_me == None:
                    with_quote = True
                    if random.random() > 0.01:
                        return

                response = self.message_chat(session, author, message)

            if response != None:
                send(update, response, with_quote=with_quote)


    def message_error(self, session, author, message):
        print('------------')
        print('SESSION')
        print(session)
        print('AUTHOR')
        print(author)
        print('MESSAGE')
        print(message)
        return None


    def message_chat(self, session, author, message):
        word     = self.reasoning(session, message)
        response = self.response(session, word)
        self.internalize(response)
        response.mind = str(self.mind)
        return response


    def reasoning(self, session, message):
        if random.random() < 0.5:
            reasoning = str(self.mind)
        else:
            reasoning = message.content

        words = []
        for word in re.split('\W+', reasoning):
            if word != '':
                words.append(word)

        total   = 0
        entries = Dictionary.fetch_scores(session, words)
        for entry in entries:
            total += entry.score

        word       = ''
        rand_value = random.random() * total
        for entry in entries:
            total -= entry.score
            if total < rand_value:
                word = entry.word
                break
        
        return word


    def response(self, session, word):
        rand_value = random.random()

        if rand_value < 0.001:
            response         = Message()
            response.type    = Message.TYPE_TEXT
            response.content = str(self.mind).capitalize()
            
            rand_value = random.random()

            if rand_value < (1.0 / 3.0):
                response.content += '.'

            elif rand_value < (2.0 / 3.0):
                response.content += '!'

            else:
                response.content += '?'

        elif rand_value < 0.1:
            response = Message.fetch_random(session)

        elif rand_value < 0.3:
            response = Message.fetch_document(session, word)

        elif rand_value < 0.5:
            response = Message.fetch_sticker(session, word)

        else:
            response = Message.fetch_word(session, word)

        return response


    def memorizable(self, message):
        if '4chan.org' in message.content:
            return False
        if '4cdn.org' in message.content:
            return False
        return True


    def internalize(self, message):
        try:
            for word in re.split('\W+', message.mind):
                self.mind.add(word)
        except:
            pass

        if message.type == Message.TYPE_TEXT:
            for word in re.split('\W+', message.content):
                self.mind.add(word)


    def run(self):
        # If testing, don't poll old results.
        self.updater.start_polling(clean=(self.metadata.first_name == "Betamiko"))
        self.updater.idle()



import os
import random
import re

from sqlalchemy     import create_engine
from sqlalchemy.orm import sessionmaker
from telegram.ext   import Updater

from .telegram import *
from .database import *
from .command  import command



class Main:
    def __init__(self, config):
        self.config   = config
        self.Session  = sessionmaker(bind=create_engine('sqlite:///data/database.sqlite'))
        self.updater  = Updater(token=config.token)
        self.metadata = self.updater.bot.get_me()
        self.handler  = UpdateHandler(self.metadata, self.message)
        self.mind     = []

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
                response = self.message_command(session, author, message)

            else:
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


    def message_command(self, session, author, message):
        return command(session, author, message)


    def message_chat(self, session, author, message):
        message.mind = ' '.join(self.mind)
        session.add(message)

        if re.search(self.metadata.first_name, message.content, re.IGNORECASE) == None:
            with_quote = True
            # 10% chance of answering random messages on the channel
            if random.random() > 0.01:
                return

        rand_value = random.random()

        if rand_value < 0.1:
            response = Message.fetch_random(session)

        elif rand_value < 0.3:
            words    = re.split('\s+', message.content)
            selected = words[int(random.random() * len(words))]
            response = Message.fetch_document(session, selected)

        elif rand_value < 0.5:
            words    = re.split('\s+', message.content)
            selected = words[int(random.random() * len(words))]
            response = Message.fetch_sticker(session, selected)

        else:
            words    = re.split('\s+', message.content)
            selected = words[int(random.random() * len(words))]
            response = Message.fetch_word(session, selected)

        return response


    def run(self):
        # If testing, don't poll old results.
        self.updater.start_polling(clean=(self.metadata.first_name == "Betamiko"))
        self.updater.idle()



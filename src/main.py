import os
import random

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

    def message(self, api, update, error=None):
        with scoped_session(self.Session) as session:
            author  = read_author(update)
            message = read_message(update)

            if message.type == Message.TYPE_COMMAND:
                response = command(message)

            else:
                session.merge(author, message)

                rand_value = random.random()
                response   = Message.random(session)

            send(update, response)

    def run(self):
        # If testing, don't poll old results.
        self.updater.start_polling(clean=(self.metadata.name == "Betamiko"))
        self.updater.idle()


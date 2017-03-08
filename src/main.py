import os
import sqlite3

from telegram.ext import Updater

from .database import MessageTable, Message
from .telegram import UpdateHandler

class Main:
    def __init__(self, config):
        self.config   = config
        self.database = sqlite3.connect(os.path.join('data', 'database.db'))
        self.updater  = Updater(token=config.token)
        self.metadata = self.updater.bot.get_me()
        self.handler  = UpdateHandler(self.metadata, self.message)
        self.mind     = ''

        self.updater.dispatcher.add_handler(self.handler)
        self.updater.dispatcher.add_error_handler(self.handler.error_handler)

    def __del__(self):
        try:
            self.database.close()
        except:
            pass

    def message(self, api, update, error=None):
        messages = MessageTable(self.database)
        incoming = Message.factory(update, mind=self.mind)
        outgoing = messages.search(incoming.content())
        outgoing.send(api)

    def run(self):
        # If testing, don't poll old results.
        self.updater.start_polling(clean=(self.metadata.name == "Betamiko"))
        self.updater.idle()



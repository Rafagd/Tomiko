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


    def message(self, api, update, error=None):
        with scoped_session(self.Session) as session:
            author     = read_author(update)
            response   = None
            with_quote = False

            try:
                # Tries to find one, raises an exception if it doesn't.
                Author.fetch(session, author.id)
            except:
                session.add(author)

            if error == None:
                try:
                    message = read_message(update)
                except:
                    print('ERRO!')
                    print(update)
                    raise
            else:
                message = read_error(error)

            if message.type == Message.TYPE_ERROR:
                print(message)
                return

            elif message.type == Message.TYPE_COMMAND:
                response = command(session, author, message)

            else:
                message.author_id = author.id
                message.mind      = ' '.join(self.mind)
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

            if response != None:
                send(update, response, with_quote=with_quote)


    def run(self):
        # If testing, don't poll old results.
        self.updater.start_polling(clean=(self.metadata.name == "Betamiko"))
        self.updater.idle()



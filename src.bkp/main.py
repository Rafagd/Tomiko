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

        self.update_tick   = 0
        self.last_response = None


    def message(self, api, update, error = None):
        with scoped_session(self.Session) as session:

            if self.update_tick == 0:
                print('Updating dictionary')
                Dictionary.update(session)
                self.update_tick = 250
                print('Updated')

            self.update_tick -= 1

            author     = read_author(update, session)
            message    = read_message(update, error)
            response   = None
            with_quote = False

            if message.type == Message.TYPE_ERROR:
                response = self.message_error(session, author, message)

            elif message.type == Message.TYPE_COMMAND:
                response = command(self, session, author, message)

            else:
                if message.type == Message.TYPE_TEXT:
                    self.internalize(session, message.content)
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

                if mentions_me != None:
                    response.why.append('mentions_me')
                elif with_quote:
                    response.why.append('random_answer')

                self.last_response = response

            if response != None:
                try:
                    send(update, response, with_quote=with_quote)
                except:
                    print('ERROR SENDING: ' + str(response))


    def message_error(self, session, author, message):
        response         = Message()
        response.content = 'ERROR: ' + message
        response.mind    = self.mind
        response.why     = [ str(message), 'error' ]
        return response


    def message_chat(self, session, author, message):
        mind_str = str(self.mind)

        if random.random() < 0.5:
            content = mind_str
            why     = 'from_mind'
        else:
            content = message.content
            why     = 'from_text'

        try:
            word = self.random_words_with_scale(session, self.split_words(content), quantity=1)[0]
        except:
            word = ''

        self.internalize(session, content)
        self.internalize(session, mind_str)

        response       = self.response(session, word)
        response.mind  = mind_str
        response.why  += [ content, why ]
        return response


    def split_words(self, content):
        words = []
        
        try:
            for word in re.split('\W+', content):
                if word != '':
                    words.append(word)
        except:
            pass

        return words
    

    def random_words_with_scale(self, session, words, quantity):
        total   = 0
        entries = Dictionary.fetch_scores(session, words)
        for entry in entries:
            total += entry.score

        words  = []
        values = []

        for i in range(quantity):
            values.append(random.random() * total)

        # Ascending order because we are popping values.
        values.sort()

        try:
            value = values.pop()

            # Just run until one of the pops raises a IndexError.
            while True:
                entry  = entries.pop()
                total -= entry.score
                if total < value:
                    words.append(entry.word)
                    value = values.pop()

        except IndexError:
            pass

        return words


    def response(self, session, word):
        rand_value = random.random()

        if rand_value < 0.001:
            response         = Message()
            response.type    = Message.TYPE_TEXT
            response.content = str(self.mind).capitalize()
            
            rand_value = random.random()

            if rand_value < (1.0 / 3.0):
                response.content += '.'
                response.why      = [ 'period', 'response_mind' ]

            elif rand_value < (2.0 / 3.0):
                response.content += '!'
                response.why      = [ 'exclamation', 'response_mind' ]

            else:
                response.content += '?'
                response.why      = [ 'question', 'response_mind' ]

        elif rand_value < 0.1:
            response = Message.fetch_random(session)
            response.why.append('response_random')

        elif rand_value < 0.3:
            response = Message.fetch_document(session, word)
            response.why.append('response_document')

        elif rand_value < 0.5:
            response = Message.fetch_sticker(session, word)
            response.why.append('response_sticker')

        else:
            response = Message.fetch_word(session, word)
            response.why.append('response_text')

        return response


    def memorizable(self, message):
        banned = [ '4chan.org', '4cdn.org' ]

        for word in banned:
            if word in message.content:
                return False

        return True


    def internalize(self, session, content):
        words = self.split_words(content)

        if len(words) < 3:
            count = len(words)
        else:
            count = max(3, int(random.random() * len(words)))

        words = self.random_words_with_scale(session, words, count)
        
        try:
            for i in range(count):
                word = words[int(random.random() * len(words))]
                if words != '':
                    self.mind.add(word)
        except:
            # May IndexError sometimes, just ignore it. It's ok.
            pass


    def run(self):
        # If testing, don't poll old results.
        self.updater.start_polling(clean=(self.metadata.first_name == "Betamiko"))
        self.updater.idle()



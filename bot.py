import logging
import re
import log

from bank import PhraseBank 

logger = logging.getLogger("Bot")

class Bot:
    def __init__(self, name):
        self.name   = name
        self.regexp = re.compile("(?is)" + name)
        self.log    = log.Log("phrases.log")
        self.index  = log.Index(self.log)


    def listen(self, person, message):
        # Receives an escaped version of the message, and the number of times
        # it replaced the name of the bot for {nome}
        message, subs = regexp.subn("{nome}", message.replace("{", "{{").replace("}", "}}"))
        message = log.Message(message, self.log.size + 1)
        self.log.add(message)

        response = ""
        if subs > 0:
            response = self.reply(person, message)

        self.index.update(message)
        return response


    def reply(self, person, message):
        return self.bank.read_weighted(message).format(nome=person)



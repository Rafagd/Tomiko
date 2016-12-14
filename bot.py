import logging
import re

from bank import PhraseBank 

logger = logging.getLogger("Bot")

class Bot:
    def __init__(self, name):
        self.bank   = PhraseBank()
        self.name   = name
        self.maintenance()


    def maintenance(self):
        logger.info("Starting maintenance")
        self.bank.word_indexing()
        self.bank.word_scaling()
        logger.info("Maintenance ended")


    def listen(self, person, message):
        message = re.sub(r"(?is)" + self.name, "{nome}",
            message.replace("{", "{{").replace("}", "}}")
        )
        self.bank.add(message)

        if message.find("{nome}") >= 0:
            return self.reply(person, message)

        return ""


    def reply(self, person, message):
        return self.bank.read_weighted(message).format(nome=person)


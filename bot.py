import re

from bank import PhraseBank 

class Bot:
    def __init__(self, name):
        self.bank   = PhraseBank()
        self.name   = name
        self.regexp = re.compile(".*" + name + ".*", re.IGNORECASE)

    def listen(self, person, message):
        self.bank.add(re.sub(r"(?is)" + self.name, "{nome}",
            message
                .replace("{", "{{")
                .replace("}", "}}")
        ))

        if self.regexp.match(message):
            return self.reply(person)

        return ""

    def reply(self, person):
        return self.bank.read_random().format(nome=person)


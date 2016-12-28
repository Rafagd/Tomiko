import logging
import re
import random
import log

logger = logging.getLogger("Bot")

class Bot:
    def __init__(self, name):
        self.name   = name
        self.regexp = re.compile("(?is)" + name)
        self.log    = log.Log("phrases.log")
        self.index  = log.Index(self.log)
        self.mind   = Mind()


    def listen(self, person, message):
        # Receives an escaped version of the message, and the number of times
        # it replaced the name of the bot for {nome}
        message = message.replace("{", "{{").replace("}", "}}")
        m, subs = self.regexp.subn("{nome}", message)
        message = log.Message(m, self.log.size + 1)
        self.log.add(message)

        response = ""
        if subs > 0:
            response = self.reply(message).text.format(nome=person)
        elif random.random() < 0.01:
            response = self.reply(message).text.format(nome=person)

        self.index.update(message)
        self.mind.update(message)
        return response


    def reply(self, message):
        mindset  = self.mind.messages()
        mindlen  = len(mindset)
        selected = int((len(mindset) + 2) * random.random())

        if selected < mindlen:
            response = self.reply_message(mindset[selected])
        elif selected == mindlen:
            response = self.reply_message(message)
        else:
            response = self.reply_random()

        self.mind.update(response)
        return response


    def reply_random(self):
        return self.log.read_message(int(random.random() * self.log.size))


    def reply_word(self, word):
        offsets = self.index.offsets(word)
        return self.log.read_message(offsets[int(random.random() * len(offsets))])


    def reply_message(self, message):
        scale_sum = 0
        for word in message.components:
            scale = self.index.scale(word)
            if scale > 0:
                scale_sum += 1.0 / scale
            
        selected = random.random() * scale_sum
        for word in message.components:
            scale = self.index.scale(word)
            if scale > 0:
                scale_sum -= 1.0 / scale
            if selected > scale_sum:
                return self.reply_word(word)
        
        # Unreachable?
        return self.reply_random()
            

class Mind:
    def __init__(self):
        self._state = dict()


    def update(self, message):
        for word in self._state:
            self._state[word]["ttl"] -= 1

        for word in message.components:
            self._state[word] = {
                "message": log.Message(word, message.offset),
                "ttl":     10,
            }

        new_state = dict()
        for word in self._state:
            if self._state[word]["ttl"] >= 0:
                new_state[word] = self._state[word]
        self._state = new_state


    def messages(self):
        return [ self._state[word]["message"] for word in self._state ]

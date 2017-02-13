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
        self.why    = ""


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
        reply_type = random.random()
        response   = ""

        # Mente vazia faz o número nunca ser maior que 60%.
        if self.mind.empty:
            reply_type *= 0.6

        # 10% chance of random message.
        if reply_type < 0.10:
            response = self.reply_random()
            self.why = "Sei lá, respondi aquilo só pelo caos."

        # 50% of direct reply
        # (the number is 60 because it includes the prev. 10%)
        elif reply_type < 0.60:
            response = self.reply_message(message)
            self.why = "Estava respondendo esta mensagem: \"" + message.text + "\"."

        # 40% chance of mindset reply
        else:
            mindset  = self.mind.messages()
            selected = int(len(mindset) * random.random())
            response = self.reply_message(mindset[selected])
            self.why = "Pensei que tinha relação com \"" + mindset[selected].text + "\"."

        self.why = self.why.replace(nome=self.name)
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
        self.empty  = True
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
        self.empty  = False


    def messages(self):
        return [ self._state[word]["message"] for word in self._state ]


    def __str__(self):
        content = "TTL\tWord"
        ordered = sorted(self._state, key=attrgetter('ttl'), reverse=True)
        for word in ordered:
            content += "{}\t{}\n".format(ordered[word]["ttl"], word)
        return content

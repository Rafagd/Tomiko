import logging
import log
import mind
import operator
import random
import re

from reply import *

logger = logging.getLogger("Bot")

class Bot:
    def __init__(self, name):
        self.name   = name
        self.regexp = re.compile("(?is)" + name)

        self.message_log   = log.Log("data/message.log")
        self.message_index = log.Index(self.message_log)

        self.gif_log   = log.Log("data/gif.log")
        self.gif_index = log.Index(self.gif_log)

        self.mind = mind.Mind()
        self.why  = ""


    def listen_message(self, person, message):
        # Receives an escaped version of the message, and the number of times
        # it replaced the name of the bot for {nome}
        message = message.replace("{", "{{").replace("}", "}}")
        m, subs = self.regexp.subn("{nome}", message)
        message = log.Message(m, self.message_log.size + 1)
        self.message_log.add(message)

        response = NoReply()
        if subs > 0 or random.random() < 0.01:
            response = self.reply(message)
            response.set_target(person)

        self.message_index.update(message)
        self.mind.update(message)
        return response


    def listen_gif(self, person, gif):
        mind_message = ""
        for message in self.mind.messages():
            mind_message += message.text + " "
        mind_message = gif + "\t" + mind_message.rstrip()
        mind_message = log.Message(mind_message, self.gif_log.size + 1)
        print(mind_message)
        self.gif_log.add(mind_message)

        response = NoReply()
        if random.random() < 0.01:
            response = self.reply(mind_message)
            response.set_target(person)

        self.gif_index.update(mind_message)
        return response


    def reply(self, message):
        reply_type = random.random()
        response   = NoReply()

        # Mente vazia faz o número nunca ser maior que 60%.
        if self.mind.empty:
            reply_type *= 0.6

        # 10% chance of random message.
        if reply_type < 0.10:
            response = MessageReply(self.read_random(self.message_log))
            self.why = "Sei lá, respondi aquilo só pelo caos."

        # 20% chance of replying with gif
        if reply_type < 0.3:
            response = self.reply_gif()
            # self.why is filled inside the function.

        # 50% of direct reply
        elif reply_type < 0.70:
            response = MessageReply(
                self.read_message(self.message_log, self.message_index, message)
            )
            self.why = "Estava respondendo esta mensagem: \"" + message.text + "\"."

        # 40% chance of mindset reply
        else:
            response = MessageReply(
                self.read_mind(self.message_log, self.message_index)
            )
            # self.why is filled inside the function.

        self.mind.update(response.message)
        return response


    def reply_gif(self):
        if random.random() < 0.20:
            message  = self.read_random(self.gif_log)
            self.why = "Achei esse gif bonitinho."
        else:
            message = self.read_mind(self.gif_log, self.gif_index)
            # self.why is set inside the function
        return GifReply(message)


    def read_random(self, log):
        rand = int(random.random() * log.size)
        return log.read_message(rand)


    def read_word(self, log, index, word):
        offsets = index.offsets(word)
        return log.read_message(offsets[int(random.random() * len(offsets))])


    def read_message(self, log, index, message):
        scale_sum = 0
        for word in message.components:
            scale = index.scale(word)
            if scale > 0:
                scale_sum += 1.0 / scale
            
        selected = random.random() * scale_sum
        for word in message.components:
            scale = index.scale(word)
            if scale > 0:
                scale_sum -= 1.0 / scale
            if selected > scale_sum:
                return self.read_word(log, index, word)
        
        # Unreachable?
        return self.read_random(log)
    

    def read_mind(self, log, index):
        mindset = self.mind.messages()
        
        if len(mindset) > 0:
            selected = int(len(mindset) * random.random())
            self.why = "Pensei que tinha relação com \"" + mindset[selected].text + "\"."
            message  = self.read_message(log, index, mindset[selected])
        else:
            self.why = "Minha cabeça estava vazia."
            message  = self.read_random(log)

        # Only a problem on startup
        return message
        


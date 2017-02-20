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

        self.gif_log   = log.Log("data/gif.log", always_flush=True)
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
            response.quote_msg = (subs == 0) # Only quote if bot is interrupting

        self.message_index.update(message)
        
        # How many words we're going to remember?
        msg_count = int(5.0 * random.random() + 1.0)
        msg_list  = self.scaled_list(self.message_index, [ message ], msg_count)
        self.mind.update(msg_list)
        return response


    def listen_gif(self, person, gif):
        mind_message = ""
        for message in self.mind.messages():
            mind_message += message.text + " "
        mind_message = gif + "\t" + mind_message.rstrip()
        mind_message = log.Message(mind_message, self.gif_log.size + 1)
        self.gif_log.add(mind_message)

        response = NoReply()
        if random.random() < 0.01:
            response = self.reply(mind_message)
            response.target = person

        self.gif_index.update(mind_message)
        return response


    def reply(self, message):
        reply_type = random.random()
        response   = NoReply()

        # Mente vazia faz o número nunca ser maior que 60%.
        if self.mind.empty:
            reply_type *= 0.6

        # 10% chance of random message.
        if reply_type < 1:
            str_msg  = " ".join([ message.text for message in self.mind.messages() ]).capitalize() + "."
            response = MessageReply(log.Message(str_msg, 0))
            self.why = "Buguei."

        elif reply_type < 0.10:
            response = MessageReply(self.read_random(self.message_log))
            self.why = "Sei lá, respondi aquilo só pelo caos."

        # 20% chance of replying with gif
        elif reply_type < 0.3:
            response = self.reply_gif(message)
            # self.why is filled inside the function.

        # 50% of direct reply
        elif reply_type < 0.70:
            response = MessageReply(self.read_messages(self.message_log, self.message_index, [ message ]))
            self.why = 'Estava respondendo esta mensagem: "{}".'.format(message.text)

        # 40% chance of mindset reply
        else:
            response = MessageReply(self.read_messages(self.message_log, self.message_index, self.mind.messages()))
            # self.why is filled inside the function.

        self.mind.update([ response.message ])
        return response


    def reply_gif(self, message=""):
        selected = random.random()

        if selected < 0.20:
            message  = self.read_random(self.gif_log)
            self.why = 'Achei esse gif bonitinho.'

        if selected < 0.60 and message != "":
            message = self.read_messages(self.gif_log, self.gif_index, [ message ])
            self.why = 'Usei o gif para responder à esta frase: "{}".'.format(message.text)

        else:
            message = self.read_messages(self.gif_log, self.gif_index, self.mind.messages())
            # self.why is set inside the function
        return GifReply(message)


    def scaled_list(self, index, messages, count):
        word_stack = []
        scale_sum  = 0

        for message in messages:
            for word in message.components:
                scale = index.scale(word)
                if scale > 0:
                    scale      = 1.0 / scale
                    scale_sum += scale
                    word_stack.append((Message(word, message.offset), scale))

        result   = []
        visited  = []
        found    = 0
        expected = min(count, len(word_stack))
        selected = random.random() * scale_sum

        while found < expected:
            word = word_stack.pop()
            visited.append(word)
            scale_sum -= word[1]

            if selected > scale_sum:
                result.append(visited.pop()[0])

                while visited:
                    word       = visited.pop()
                    scale_sum += word[1]
                    word_stack.append(word)
                selected = random.random() * scale_sum
                found += 1

        return result


    def read_random(self, log):
        rand = int(random.random() * log.size)
        return log.read_message(rand)


    def read_word(self, log, index, word):
        offsets = index.offsets(word)
        return log.read_message(offsets[int(random.random() * len(offsets))])


    def read_messages(self, log, index, messages):
        scaled = self.scaled_list(index, messages, 1)
        size   = len(scaled)
        if size == 0:
            return self.read_random(log)
        selected = int(size * random.random())
        return self.read_word(log, index, scaled[selected].text)


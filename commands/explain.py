import random

class Command:
    def __init__(self, bot):
        self.trigger = "explain"
        self.bot     = bot


    def impl(self, args=[]):
        if random.random() < 0.1:
            return "Não devo explicações a ninguém."
        else:
            return self.bot.why


    def run(self, api, update, args):
        api.sendMessage(
            chat_id=update.message.chat_id,
            text=self.impl()
        )

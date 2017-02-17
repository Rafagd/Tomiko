import random

class Command:
    def __init__(self, bot):
        self.trigger = "mind"
        self.bot     = bot


    def impl(self, args=[]):
        if random.random() < 0.1:
            return "Sai da minha cabeça!"
        else:
            return "{}'s mind:\n{}".format(self.bot.name, self.bot.mind)


    def run(self, api, update, args):
        api.send_message(
            chat_id=update.message.chat_id,
            text=self.impl()
        )

#!/usr/bin/python3

import commands
import logging

from bot import Bot
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import CommandHandler
from telegram.ext import Updater


class Program:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)

        with open("token.tok") as f:
            token = f.read().rstrip()

        self.updater = Updater(token=token)
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, self.message))

        self.bot      = Bot(self.updater.bot.getMe().first_name)
        self.commands = [] # Just to make sure the GC will not collect the commands.

        for command in commands.__all__:
            cmd = getattr(commands, command).Command(self.bot)
            self.commands.append(cmd)
            self.updater.dispatcher.add_handler(
                CommandHandler(cmd.trigger, cmd.run, pass_args=True)
            )


    def message(self, api, update):
        reply = self.bot.listen(update.message.from_user.first_name, update.message.text)
        if reply != "":
            update.message.reply_text(reply)


    def main(self):
        self.updater.start_polling()
        #self.updater.idle() -- In theory handles CTRL+C, but actually makes me type it twice to quit.


if __name__ == '__main__':
    Program().main()


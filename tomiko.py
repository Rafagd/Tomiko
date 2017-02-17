#!/usr/bin/python3

import commands
import logging

from bot import Bot
from ext import GifHandler
from telegram.ext import Filters
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Updater

class Program:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)

        with open("data/token.tok") as f:
            token = f.read().rstrip()

        self.updater = Updater(token=token)
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, self.message))
        self.updater.dispatcher.add_handler(GifHandler(Filters.text, self.gif))
        self.updater.dispatcher.add_error_handler(self.error)

        self.bot      = Bot(self.updater.bot.get_me().first_name)
        self.chats    = {}
        self.commands = [] # Just to make sure the GC will not collect the commands.

        for command in commands.__all__:
            cmd = getattr(commands, command).Command(self.bot)
            self.commands.append(cmd)
            self.updater.dispatcher.add_handler(
                CommandHandler(cmd.trigger, cmd.run, pass_args=True)
            )


    def check_groups(self, message):
        chat_id = message.chat.id
        from_id = message.from_user.id
        if chat_id != from_id:
            try:
                _ = self.chats[chat_id]
            except:
                self.chats[chat_id] = chat_id


    def message(self, api, update):
        reply = self.bot.listen_message(
            update.message.from_user.first_name,
            update.message.text
        )

        reply.send(api, update.message.chat.id)
        self.check_groups(update.message)



    def gif(self, api, update):
        reply = self.bot.listen_gif(
            update.message.from_user.first_name,
            update.message.document.file_id
        )

        reply.send(api, update.message.chat.id)
        self.check_groups(update.message)


    def error(self, bot, update, error):
        logging.warning("=======================================")
        logging.warning("ERR:"+str(error))
        logging.warning("BOT:"+str(bot))
        logging.warning("UPD:"+str(update))


    def main(self):
        # If testing, don't poll old results.
        self.updater.start_polling(clean=(self.bot.name == "Betamiko"))
        self.updater.idle()
        for chat in self.chats:
            self.updater.bot.send_message(chat_id=chat, text="Fui")


if __name__ == '__main__':
    Program().main()


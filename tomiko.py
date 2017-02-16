#!/usr/bin/python3

import commands
import logging

from bot import Bot
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import CommandHandler
from telegram.ext import Updater

def get_token():
    with open("token.tok") as f:
        return f.read().rstrip()
    return ""


def message(bot, update):
    global tomiko
    reply = tomiko.listen(update.message.from_user.first_name, update.message.text)
    if reply != "":
        update.message.reply_text(reply)


logging.basicConfig(level=logging.INFO)

token  = get_token()
tomiko = Bot("Tomiko")
cmds   = [] # Just to make sure the GC will not collect the commands.

updater    = Updater(token=token)
dispatcher = updater.dispatcher
dispatcher.add_handler(MessageHandler(Filters.text, message))

for command in commands.__all__:
    cmd = getattr(commands, command).Command(dispatcher, tomiko)
    cmds.append(cmd)
    dispatcher.add_handler(CommandHandler(cmd.trigger, cmd.run, pass_args=True))

updater.start_polling()


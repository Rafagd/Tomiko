#!/usr/bin/python3

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
    reply = tomiko.listen(update.message.text)
    if reply != "":
        update.message.reply_text(reply)


logging.basicConfig(level=logging.INFO)

token  = get_token()
tomiko = Bot("Tomiko")

updater    = Updater(token=token)
dispatcher = updater.dispatcher
dispatcher.add_handler(MessageHandler(Filters.text, message))
updater.start_polling()


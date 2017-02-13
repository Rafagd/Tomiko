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
    reply = tomiko.listen(update.message.from_user.first_name, update.message.text)
    if reply != "":
        update.message.reply_text(reply)


def explain(bot, update, args):
    global tomiko
    if random.random() < 0.1:
        bot.sendMessage(
            chat_id=update.message.chat_id,
            text="Não devo explicações a ninguém."
        )
    else:
        bot.sendMessage(chat_id=update.message.chat_id, text=tomiko.why)


def mind(bot, update, args):
    global tomiko
    if random.random() < 0.1:
        bot.sendMessage(
            chat_id=update.message.chat_id,
            text="Sai da minha cabeça."
        )
    else:
        content = "Tomiko's mind:\n{}".format(bot.mind)
        bot.sendMessage(chat_id=update.message.chat_id, text=content)

logging.basicConfig(level=logging.INFO)

token  = get_token()
tomiko = Bot("Tomiko")

updater    = Updater(token=token)
dispatcher = updater.dispatcher
dispatcher.add_handler(MessageHandler(Filters.text, message))
dispatcher.add_handler(CommandHandler('explain', explain, pass_args=True))
dispatcher.add_handler(CommandHandler('mind', mind, pass_args=True))
updater.start_polling()


#!/usr/bin/python3

import logging
import random
import re
import struct
import os

from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import CommandHandler
from telegram.ext import Updater

def get_token():
    with open("token.tok") as f:
        return f.read().rstrip()
    return ""


class PhraseBank:
    def __init__(self, phrase_file=None):
        if phrase_file == None:
            phrase_file = "phrases.log"
        self.file = open(phrase_file, "ab+")
        self.file.seek(0, os.SEEK_END)
        self.size = self.file.tell()


    def __del__(self):
        if self.file:
            self.file.close()


    def add(self, text):
        self.file.seek(0, os.SEEK_END)
        self.file.write(text)
        self.size = self.file.tell()


    def read_random(self):
        result = ""

        while result == "":
            pos = int(self.size * random.random())

            while self.file.read(1) != b"\x0A":
                pos -= 1
                if pos < 0:
                    self.file.seek(0)
                    break
                self.file.seek(pos)

            result = self.file.readline()

        return bytes.decode(result)


token   = get_token()
bank    = PhraseBank()
re_name = re.compile(".*tomiko.*", re.IGNORECASE)
logging.basicConfig(level=logging.INFO)

def message(bot, update):
    global bank, re_name

    if re_name.match(update.message.text) :
        nome = update.message.from_user.first_name
        if nome == "":
            nome = update.message.from_user.username
        update.message.reply_text(bank.read_random().format(nome=nome))
        bank.add(str.encode(
            re.sub(r'(?is)tomiko', '{nome}',
                update.message.text.replace("{", "{{").replace("}", "}}") + "\x0A"
            )
        ))
    else :
        bank.add(str.encode(
            update.message.text.replace("{", "{{").replace("}", "}}") + "\x0A"
        ))

updater    = Updater(token=token)
dispatcher = updater.dispatcher
dispatcher.add_handler(MessageHandler(Filters.text, message))
updater.start_polling()


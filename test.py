#!/usr/bin/python3

import commands
import logging

from bot import Bot
from ext import OmniHandler
from telegram.ext import Updater

class Program:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)

        with open("data/token.tok") as f:
            token = f.read().rstrip()

        self.updater = Updater(token=token)
        self.updater.dispatcher.add_handler(OmniHandler(self.message))
        self.updater.dispatcher.add_error_handler(OmniHandler.error_handler(self.message))

        self.metadata = self.updater.bot.get_me()


    def message(self, api, update):
        incomming = Message.receive(self.metadata, self.update)
        outgoing  = incoming.reply()
        outgoing.send()


    def main(self):
        while True:
            message = input("")
            if message == "exit":
                break

            if message.startswith("/"):
                args          = message.split(" ")
                trigger, args = args[0][1:], args[1:]
                print(getattr(commands, trigger).Command(tomiko).impl(*args))
                continue

            response = tomiko.listen("Tester", message)
            if response != "":
                print(response)
                print(tomiko.why)



if __name__ == '__main__':
    Program().main()


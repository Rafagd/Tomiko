#!/usr/bin/python3

import bot
import commands

tomiko = bot.Bot("Tomiko")

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


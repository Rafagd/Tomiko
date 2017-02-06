#!/usr/bin/python3

import bot

tomiko = bot.Bot("Tomiko")

while True:
    message = input("")
    if message == "exit":
        break

    response = tomiko.listen("Tester", message)
    if response != "":
        print(response)
        print(tomiko.why)


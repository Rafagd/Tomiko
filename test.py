#!/usr/bin/python3

import bot

message = ""
tomiko  = bot.Bot("Tomiko")

while message != "exit":
    message  = input("")
    response = tomiko.listen("Tester", message)
    if response != "":
        print(response)


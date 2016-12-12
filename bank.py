import os
import random

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
        self.file.write(str.encode(text) + b"\x0A")
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


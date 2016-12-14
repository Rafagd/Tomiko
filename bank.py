import json
import os
import random
import re

SEPARATORS = "[ ,.!?\"':\\[\\]\n\r\t]+"

class PhraseBank:
    def __init__(self, phrase_file="phrases.log"):
        self.file   = open(phrase_file, "ab+")
        self.file.seek(0, os.SEEK_END)
        self.size   = self.file.tell()

        self._index = dict()
        self.word_indexing()

        self._scale = dict()
        self.word_scaling()


    def __del__(self):
        if self.file:
            self.file.close()


    def add(self, text):
        self.file.seek(0, os.SEEK_END)
        self.file.write(str.encode(text) + b"\x0A")
        self.size = self.file.tell()


    def word_scale(self, word):
        try:
            return self._scale[word.lower()]
        except:
            return 0


    def word_index(self, word):
        try:
            return self._index[word.lower()]
        except:
            return list()


    def read_weighted(self, message):
        words = re.split(SEPARATORS, message.lower())

        weight_sum = 0
        for word in words:
            scale = self.word_scale(word)
            if scale > 0:
                weight_sum += 1.0 / scale

        response = ""
        selected = weight_sum * random.random()
        for word in words:
            scale = self.word_scale(word)
            if scale > 0:
                weight_sum -= 1.0 / scale
            if selected > weight_sum:
                response = self.read_word(word)
                break

        for word in words:
            if word != "":
                self.update_index(word, self.file.tell() - 1)
                self.update_scale(word)

        return response


    def read_word(self, word):
        index = self.word_index(word)
        pos   = int(len(index) * random.random())
        if pos >= 0:
            return self.read(index[pos])
        return ""


    def read_random(self):
        result = ""
        while result == "":
            result = self.read(self.size * random.random())
        return result


    def read(self, pos):
        while self.file.read(1) != b"\x0A":
            pos -= 1

            if pos < 0:
                self.file.seek(0)
                break

            self.file.seek(pos)

        return bytes.decode(self.file.readline())


    def word_indexing(self):
        self._index = dict()
        self.file.seek(0)
        for line in self.file:
            words = re.split(SEPARATORS, bytes.decode(line).lower())
            for word in words:
                self.update_index(word, self.file.tell() - len(line))


    def update_index(self, word, pos):
        index = self.word_index(word)
        if pos not in index:
            index.append(pos)
        self._index[word] = index


    def word_scaling(self):
        self._scale = dict()
        self.file.seek(0)
        for line in self.file:
            words = re.split(SEPARATORS, bytes.decode(line).lower())
            for word in words:
                self.update_scale(word)

    
    def update_scale(self, word):
        self._scale[word] = self.word_scale(word) + 1

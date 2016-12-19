import os
import re

SEPARATORS = re.compile("[ ,.!?\"':\\[\\]\n\r\t]+")

class Message:
    def __init__(self, text, offset):
        self.text       = text
        self.offset     = offset
        self.components = SEPARATORS.split(text.upper())


class Log:
    def __init__(self, file_path):
        self.file = open(file_path, "ab+")
        self.file.seek(0, os.SEEK_END)
        self.size = self.file.tell()


    def add(self, message):
        self.file.seek(0, os.SEEK_END)
        self.file.write(str.encode(message.text) + b"\x0A")
        self.size = self.file.tell()


    def iterator(self):
        pos = 0
        while pos < self.size:
            self.file.seek(pos)
            line = self.file.readline()
            yield Message(bytes.decode(line), pos)
            pos += len(line)


    def read_message(self, position):
        self.file.seek(position)

        while self.file.read(1) != b"\x0A":
            position -= 1

            if position < 0:
                position = 0
                self.file.seek(0)
                break

            self.file.seek(position)

        return Message(bytes.decode(self.file.readline()), position)


class Index:
    def __init__(self, log):
        self.scales  = dict()
        self.offsets = dict()
        for message in log.iterator():
            self.update(message)


    def update(self, message)
        for word in message.components:
            self.update_scales(word)
            self.update_offsets(word, message.offset)


    def update_scales(self, word):
        try:
            self.scales[word] += 1
        except:
            self.scales[word] = 1


    def update_offsets(self, word, offset):
        try:
            self.offsets[word].append(offset)
        except:
            self.offsets[word] = list(offset)

    

import os.path
import sqlite3
import yaml

try:
    from yaml import CLoader as yaml_loader
    from yaml import CDumper as yaml_dumper
except ImportError:
    from yaml import Loader as yaml_loader
    from yaml import Dumper as yaml_dumper

from src.database import *


current_version = 1


class Config:
    def __init__(self, data):
        global current_version

        if data == None:
            data = {
                'version': 0 if os.path.isfile(os.path.join('data', 'token.tok')) else current_version,
            }

        if int(data['version']) > current_version:
            data['version'] = current_version

        self.__dict__ = data
        self.normalize()


    def normalize(self):
        self.version = int(self.version)


    def version_changed(self):
        global current_version
        return self.version != current_version


    def migrate(self):
        global current_version
        # range[old, new)
        for i in range(self.version, current_version):
            globals()['migrate_{}_{}'.format(i, i + 1)](self)


    def load(path):
        with open(path, "r+") as stream:
            return Config(yaml.load(stream, Loader=yaml_loader))


    def save(self, path):
        with open(path, "w+") as stream:
            stream.write(yaml.dump(self.__dict__, Dumper=yaml_dumper, default_flow_style=False))


    def __repr__(self):
        return str(self.__dict__)


def migrate_0_1(config):
    database = sqlite3.connect(os.path.join('data', 'database.db'))
    authors  = AuthorTable(database)
    messages = MessageTable(database)
    slaps    = SlapTable(database)

    authors.create()
    messages.create()
    slaps.create()

    with open(os.path.join('data', 'token.tok'), 'r') as stream:
        config.token = stream.readline().rstrip()

    with open(os.path.join('data', 'message.log'), 'r') as stream:
        for line in stream:
            line = line.rstrip()
            messages.insert(TextMessage(line, mind=line))

    with open(os.path.join('data', 'gif.log'), 'r') as stream:
        for line in stream:
            data = line.rstrip().split('\t')
            doc  = data[0]
            mind = '\t'.join(data[1:])
            messages.insert(DocumentMessage(doc, mind=mind))

    with open(os.path.join('data', 'slaps.txt')) as stream:
        for line in stream:
            slaps.insert(TextSlap(line))

    database.close()
    config.version = 1

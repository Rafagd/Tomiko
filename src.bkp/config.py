import logging
import os.path
import yaml

try:
    from yaml import CLoader as yaml_loader
    from yaml import CDumper as yaml_dumper
except ImportError:
    from yaml import Loader as yaml_loader
    from yaml import Dumper as yaml_dumper

from sqlalchemy     import create_engine
from sqlalchemy.orm import sessionmaker
from src.database   import *

current_version = 2

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
        with open(path, "a+") as stream:
            stream.seek(0)
            return Config(yaml.load(stream, Loader=yaml_loader))


    def save(self, path):
        with open(path, "w+") as stream:
            stream.write(yaml.dump(self.__dict__, Dumper=yaml_dumper, default_flow_style=False))


    def __repr__(self):
        return str(self.__dict__)


def migrate_0_1(config):
    engine = create_engine('sqlite:///data/database.sqlite')

    try:
        Author.__table__.create(engine)
    except:
        pass

    try:
        Message.__table__.create(engine)
    except:
        pass

    try:
        Slap.__table__.create(engine)
    except:
        pass

    config.version = 1


def migrate_1_2(config):
    engine = create_engine('sqlite:///data/database.sqlite')

    try:
        Dictionary.__table__.create(engine)
    except:
        pass

    with scoped_session(sessionmaker(bind=engine)) as session:
        Dictionary.update(session)

    config.version = 2



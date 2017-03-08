#!/usr/bin/python3

import logging

from src.config   import Config
from src.main     import Main
from src.message  import Message

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    config_path = 'data/config.yaml'
    config = Config.load(config_path)

    if config.version_changed():
        logging.info('Version changed, migrating data.')
        config.migrate()
        config.save(config_path)
        logging.info('Migration complete.')

    Main(config).run()
    config.save(config_path)


import logging

class Logger:
    def __init__(self, debug, strict) -> None:
        logging.basicConfig(format='%(levelname)s:%(message)s')
        logging.getLogger().setLevel(logging.INFO)
        self.debug = debug
        self.strict = strict

    def info(self, message):
        if self.debug:
            logging.info(message)

    def warning(self, message):
        logging.warning(message)
        if self.strict_mode:
            exit(1)

    def error(self, message):
        logging.error(message)
        exit(1)
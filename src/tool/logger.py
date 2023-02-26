import logging

debug_mode = False
strict_mode = False

logging.basicConfig(format='%(levelname)s: %(message)s')
logging.getLogger().setLevel(logging.INFO)

class LoggerWrapper():
    def __init__(self, repl_map = {}, log = logging) -> None:
        self.repl_map = repl_map
        self.log = log
    
    def _repl(self, msg, args):
        msg = msg % args
        for symbol, repl in self.repl_map.items():
            msg = msg.replace(symbol, repl)
        return msg

    def info(self, msg, *args):
        msg = self._repl(msg, args)
        if debug_mode:
            self.log.info(msg)

    def debug(self, *args):
        self.info(*args)

    def group(self, title: str, messages: list[str]):
        self.info(f'===== {title} =====')
        for message in messages:
            self.info(message)
        self.info(f'===== {title} =====')

    def warning(self, msg, *args):
        msg = self._repl(msg, args)
        self.log.warning(msg)
        if strict_mode:
            exit(1)

    def error(self, msg, *args):
        msg = self._repl(msg, args)
        self.log.error(msg)
        exit(1)

def get_file_logger(filename: str, repl_map = {}):
    file_logger = logging.getLogger('file')
    file_handler = logging.FileHandler(filename, mode='w')
    file_logger.addHandler(file_handler)
    file_logger.propagate = False
    return LoggerWrapper(repl_map, file_logger)

logger = LoggerWrapper()

def info(msg, *args):
    logger.info(msg, *args)

def debug(msg, *args):
    logger.debug(msg, *args)

def group(msg, *args):
    logger.group(msg, *args)

def warning(msg, *args):
    logger.warning(msg, *args)

def error(msg, *args):
    logger.error(msg, *args)
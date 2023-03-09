import logging
import re

debug_mode = False
strict_mode = False

logging.basicConfig(format='%(levelname)s: %(message)s')
logging.getLogger().setLevel(logging.INFO)

class LoggingWrapper():
    def __init__(self, repl_map = {}, log = logging) -> None:
        self.repl_map = repl_map
        self.log = log
    
    def _str_repl(self, s: str) -> str:
        for pattern, repl in self.repl_map.items():
            s = s.replace(pattern, repl)
        return s

    def _args_repl(self, msg, args):
        # Spec https://docs.python.org/3/library/stdtypes.html#printf-style-string-formatting
        printf_style = r'''(?x)
        %(?:\((.*?)\))?
         (?:[#0\- +])?
         (?:\*|\d*)?
         (?:\.(?:\*|\d*))?
         (?:[hlL])?
         ([diouxXeEfFgGcrsa])
        '''
        if len(args) == 0:
            return args
        
        matches = re.findall(printf_style, msg)
        if type(args[0]) == dict:
            return ({k: self._str_repl(str(args[0][k])) 
                     for k, t in matches if t == 's'},)
        
        return tuple([self._str_repl(str(args[i])) 
                          if t == 's' else args[i] 
                          for i, (_, t) in enumerate(matches)])

    def info(self, msg, *args):
        msg = self._str_repl(msg)
        args = self._args_repl(msg, args)
        if debug_mode:
            self.log.info(msg, *args)

    def debug(self, msg, *args):
        self.info(msg, *args)

    def warning(self, msg, *args):
        msg = self._str_repl(msg)
        args = self._args_repl(msg, args)
        self.log.warning(msg, *args)
        if strict_mode:
            exit(1)

    def error(self, msg, *args):
        msg = self._str_repl(msg)
        args = self._args_repl(msg, args)
        self.log.error(msg, *args)
        exit(1)

def get_file_logger(filename: str, repl_map = {}):
    file_logger = logging.getLogger('file')
    file_handler = logging.FileHandler(filename, mode='w')
    file_logger.addHandler(file_handler)
    file_logger.propagate = False
    return LoggingWrapper(repl_map, file_logger)

logger = LoggingWrapper()

def info(msg, *args):
    logger.info(msg, *args)

def debug(msg, *args):
    logger.debug(msg, *args)

def warning(msg, *args):
    logger.warning(msg, *args)

def error(msg, *args):
    logger.error(msg, *args)
import logging
import re
from tool.constants import PLY_ERR_MSG

verbose = False
strict = False

logging.basicConfig(format='%(levelname)s: %(message)s')
logging.getLogger().setLevel(logging.INFO)

class LoggingWrapper():
    def __init__(self, repl_map: dict = {}, logger = logging, ply_repl=False):
        self.repl_map = repl_map
        self.logger = logger
        self.ply_repl = ply_repl
    
    def _repl(self, msg, args):
        msg, args = self._ply_repl(msg, args)
        args = self._args_repl(msg, args)
        msg %= args
        return self._str_repl(msg)

    def _ply_repl(self, msg, args):
        if not self.ply_repl or not msg in PLY_ERR_MSG:
            return msg, args
        else:
            new_msg, arg_idxs = PLY_ERR_MSG[msg]
            return new_msg, tuple(args[i] for i in arg_idxs)

    def _str_repl(self, s: str) -> str:
        for pattern, repl in self.repl_map.items():
            s = s.replace(pattern, repl)
        return s

    def _args_repl(self, msg, args):
        # Spec https://docs.python.org/3/library/stdtypes.html#printf-style-string-formatting
        printf_style = r'''(?x)
        %(?:\((.*?)\))?       # Mapping key
         (?:[#0\- +])?        # Conversion flags
         (?:\*|\d*)?          # Minimum field width
         (?:\.(?:\*|\d*))?    # Precision
         (?:[hlL])?           # Length modifier
         ([diouxXeEfFgGcrsa]) # Conversion type
        '''
        if len(args) == 0:
            return args
        
        matches = re.findall(printf_style, msg)
        if isinstance(args[0], dict):
            return ({k: self._str_repl(str(args[0][k])) 
                     if t == 's' else args[0][k]
                     for k, t in matches},)
        
        return tuple([self._str_repl(str(args[i])) 
                          if t == 's' else args[i] 
                          for i, (_, t) in enumerate(matches)])

    def info(self, msg, *args):
        msg = self._repl(msg, args)
        if verbose:
            self.logger.info(msg)

    def debug(self, msg, *args):
        self.info(msg, *args)

    def warning(self, msg, *args):
        msg = self._repl(msg, args)
        self.logger.warning(msg)
        if strict:
            exit(1)

    def error(self, msg, *args):
        msg = self._repl(msg, args)
        self.logger.error(msg)
        exit(1)

def get_file_logger(filename: str, *args, **kwargs):
    file_logger = logging.getLogger('file')
    file_handler = logging.FileHandler(filename, mode='w', delay=True)
    file_logger.addHandler(file_handler)
    file_logger.propagate = False
    return LoggingWrapper(*args, logger=file_logger, **kwargs)

logger = LoggingWrapper()

def info(msg, *args):
    logger.info(msg, *args)

def debug(msg, *args):
    logger.debug(msg, *args)

def warning(msg, *args):
    logger.warning(msg, *args)

def error(msg, *args):
    logger.error(msg, *args)
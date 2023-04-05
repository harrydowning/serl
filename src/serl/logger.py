import logging
import re
from serl.constants import PLY_ERR_MSG

verbose = False
error_seen = False

logging.basicConfig(format='%(levelname)s: %(message)s')
logging.getLogger().setLevel(logging.INFO)

class LoggingWrapper():
    def __init__(self, logger = logging, *, verbose=None, repl_map={}, 
                 ply_repl=False):
        self.logger = logger
        self.verbose = verbose
        self.repl_map = repl_map
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

    def info(self, msg, *args, important=False):
        msg = self._repl(msg, args)
        should_show = self.verbose if self.verbose != None else verbose
        if should_show or important:
            self.logger.info(msg)

    def debug(self, msg, *args, **kwargs):
        self.info(msg, *args, **kwargs)

    def warning(self, msg, *args):
        msg = self._repl(msg, args)
        self.logger.warning(msg)

    def error(self, msg, *args, code=0):
        msg = self._repl(msg, args)
        self.logger.error(msg) 
        global error_seen
        error_seen = True
        if code:
            exit(code)

def get_file_logger(filename: str, **kwargs):
    file_logger = logging.getLogger('file')
    file_handler = logging.FileHandler(filename, mode='w', delay=True)
    file_logger.addHandler(file_handler)
    file_logger.propagate = False
    return LoggingWrapper(file_logger, **kwargs)

logger = LoggingWrapper()

def info(msg, *args, **kwargs):
    logger.info(msg, *args, **kwargs)

def debug(msg, *args, **kwargs):
    logger.debug(msg, *args, **kwargs)

def warning(msg, *args):
    logger.warning(msg, *args)

def error(msg, *args, **kwargs):
    logger.error(msg, *args, **kwargs)
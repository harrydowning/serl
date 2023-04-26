import re
import platform

import serl.logger as logger

import ply.lex as lex
import regex

implementation = platform.python_implementation()
using_cpython = implementation == 'CPython'

class SerlToken(tuple):
    def __new__(cls, lineno, col, captures):
        return super(SerlToken, cls).__new__(cls, (*captures,))
    
    def __init__(self, lineno, col, *captures):
        super().__init__()
        self.lineno = lineno
        self.col = col

def get_pattern_func(token, pattern, using_regex, flag_value):
    def f(t):  
        span = t.lexer.lexmatch.span()
        lineno = t.lexer.lineno
        col = (span[0] + 1) - getattr(t.lexer, 'lastlinepos', 0)
        for m in lex.re.finditer(pattern, t.lexer.lexdata, flag_value):
            if span != m.span():
                continue
            if using_regex and using_cpython:
                t.value = SerlToken(lineno, col, m.allcaptures())
                break
            else:
                t.value = SerlToken(lineno, col, (m.group(), *m.groups()))
                break

        string = t.lexer.lexdata[span[0]:span[1]]
        newlines = string.count('\n')
        if newlines:
            t.lexer.lineno += newlines
            t.lexer.lastlinepos = t.lexer.lexpos
        return t
    
    f.__doc__ = pattern
    f.__name__ = token
    return f

def newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    t.lexer.lastlinepos = t.lexer.lexpos

def t_error(t):
    logger.error(f'Illegal character \'{t.value[0]}\' on line '
                 f'{t.lexer.lineno}.')

def get_ignore_func(pattern):
    def f(t): pass
    f.__name__ = 'ignore'
    f.__doc__ = pattern
    return f

def get_whole_match(token):
    if isinstance(token.value[0], list):
        return token.value[0][0]
    else:
        return token.value[0]

def get_flag_value(using_regex, flags):
    if using_regex:
        if using_cpython:
            lex.re = regex
        else:
            logger.error(f'Use of \'regex\' package requires \'CPython\' '
                         f'implementation. Current implementation: '
                         f'\'{implementation}\'.', code=1)
    
    flag_value = re.NOFLAG
    for flag_str in re.split(r'\s+', flags.strip()):
        try:
            flag = getattr(lex.re, flag_str)
            if isinstance(flag, lex.re.RegexFlag):
                flag_value |= flag
                continue
        except AttributeError:
            pass
        logger.warning(f'Can\'t find regex flag \'{flag_str}\'.')
    return flag_value

def build_lexer(_tokens: dict[str, str], token_map: dict[str,str], ignore: str,
                using_regex: bool, flags: str, default: bool): 
    flag_value = get_flag_value(using_regex, flags)
    
    g = globals()
    g['tokens'] = ('default',) if default else ()

    for token, pattern in _tokens.items():
        token_name = token_map[token]

        g['tokens'] = (*g['tokens'], token_name)
        g[f't_{token_name}'] = get_pattern_func(token, pattern, using_regex, 
                                                flag_value)

    # Lower precedence than user rules
    g['t_newline'] = newline
    if ignore != None:
        g['t_ignore_func'] = get_ignore_func(ignore)
    
    if default:
        g['t_default'] = '.'
    
    errorlog = logger.LoggingWrapper(ply_repl=True)
    return lex.lex(errorlog=errorlog, reflags=flag_value)

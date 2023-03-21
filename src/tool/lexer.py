import re, regex
import tool.logger as logger
import ply.lex as lex
import platform

implementation = platform.python_implementation()
using_cpython = implementation == 'CPython'

def get_pattern_function(token, pattern, using_regex):
    def f(t):
        s, e = t.lexer.lexmatch.span()
        string = t.lexer.lexmatch.string[s:e]
        # Obtain capture groups
        if using_regex and using_cpython:
            m = regex.match(pattern, string, regex.VERBOSE)
            t.value = m.allcaptures()
        else:
            m = re.match(pattern, string, re.VERBOSE)
            t.value = (m.group(), *m.groups())
        t.lexer.lineno += string.count('\n')
        return t
    
    f.__doc__ = pattern
    f.__name__ = token
    return f

def newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    logger.warning(f'Illegal character \'{t.value[0]}\' on line '
                   f'{t.lexer.lineno}.')

def get_ignore_func(pattern):
    def f(t): pass
    f.__name__ = 'ignore'
    f.__doc__ = pattern
    return f

def build_lexer(_tokens: dict[str, str], token_map: dict[str,str], ignore: str,
                using_regex: bool):
    g = globals()
    g['tokens'] = ()

    for token, pattern in _tokens.items():
        token_name = token_map[token]

        g['tokens'] = (*g['tokens'], token_name)
        g[f't_{token_name}'] = get_pattern_function(token, pattern, using_regex)

    # TODO g['t_DEFAULT'] = r'.'
    # Lower precedence than user rules
    g['t_newline'] = newline
    if ignore != None:
        g['t_ignore_func'] = get_ignore_func(ignore)
    
    if using_regex:
        if using_cpython:
            lex.re = regex
        else:
            logger.error(f'Use of \'regex\' package requires \'CPython\' '
                         f'implementation. Current implementation: '
                         f'\'{implementation}\'.')
    
    errorlog = logger.LoggingWrapper(ply_repl=True)
    return lex.lex(errorlog=errorlog)

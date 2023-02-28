import re, regex
import tool.logger as logger
import ply.lex as lex
import platform

implementation = platform.python_implementation()
using_cpython = implementation == 'CPython'

def get_pattern_function(pattern, using_regex):
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
    return f

def newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

def build_lexer(_tokens: dict[str, str], token_map: dict[str,str], 
                ignore: str, using_regex: bool):
    g = globals()
    g['tokens'] = () # TODO ('DEFAULT',)

    for token, pattern in _tokens.items():
        token_name = token_map[token]

        g['tokens'] = (*g['tokens'], token_name)
        g[f't_{token_name}'] = get_pattern_function(pattern, using_regex)

    # TODO g['t_DEFAULT'] = r'.'
    # Lower precedence than user rules
    g['t_newline'] = newline
    g['t_ignore'] = ignore
    
    if using_regex:
        if using_cpython:
            lex.re = regex
        else:
            logger.error(f'Use of \'regex\' package requires \'CPython\' '
                         f'implementation. Current implementation'
                         f'\'{implementation}\'.')
    
    return lex.lex()

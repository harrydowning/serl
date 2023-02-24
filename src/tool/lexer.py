import re
import tool.logger as logger
import ply.lex as lex
# import regex

def get_pattern_function(pattern):
    def f(t):
        s, e = t.lexer.lexmatch.span()
        string = t.lexer.lexmatch.string[s:e]
        # Obtain capture groups
        m = re.match(pattern, string, re.VERBOSE)
        t.value = (string, *m.groups())
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
                ignore: str):
    g = globals()
    g['tokens'] = () #('DEFAULT',)

    for token, pattern in _tokens.items():
        token_name = token_map[token]

        g['tokens'] = (*g['tokens'], token_name)
        g[f't_{token_name}'] = get_pattern_function(pattern)

    # g['t_DEFAULT'] = r'.'
    g['t_newline'] = newline # Lower precedence than user rules
    g['t_ignore'] = ignore
    #lex.re = regex
    return lex.lex()

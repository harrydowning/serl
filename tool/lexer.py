import ply.lex as lex
import regex

# TODO: Define a couple of set functionality functions (e.g., switching lexing state)

def get_pattern_function(pattern):
    def f(t):
        s, e = t.lexer.lexmatch.span()
        string = t.lexer.lexmatch.string[s:e]
        m = regex.match(pattern, string, regex.VERBOSE)
        t.value = m.allcaptures()
        t.lexer.lineno += string.count('\n')
        return t
    
    f.__doc__ = pattern
    return f

t_DEFAULT = r'.+'

# def default(t):
#     r'(.|\n)+'
#     t.lexer.lineno += t.value.count('\n')
#     return t

def newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

def build_lexer(config: dict):
    g = globals()
    g['tokens'] = ('DEFAULT',)

    for token, pattern in config.items():
        token = token.upper()
        g['tokens'] = (*g['tokens'], token)
        g[f't_{token}'] = get_pattern_function(pattern)

    g['t_newline'] = newline # Ensures lower precedence compared to user rules
    #g['t_DEFAULT'] = default


    return lex.lex()

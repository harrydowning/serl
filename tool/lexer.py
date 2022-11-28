from types import FunctionType
import ply.lex as lex
import regex

# TODO: Define a couple of set functionality functions (e.g., switching lexing state)

def get_pattern_function(name, pattern):
    def f(t):
        s, e = t.lexer.lexmatch.span()
        string = t.lexer.lexmatch.string[s:e]
        m = regex.match(pattern, string, regex.VERBOSE)
        t.value = m.allcaptures()[1:]
        t.lexer.lineno += string.count('\n')
        return t
    
    pattern_function = FunctionType(f.__code__, f.__globals__, name, f.__defaults__, f.__closure__)
    pattern_function.__doc__ = pattern
    return pattern_function

t_DEFAULT = r'.+'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

def build_lexer(config: dict):
    g = globals()
    g['tokens'] = ('DEFAULT')

    for token, pattern in config.get('rules', []):
        token = token.upper()
        name = f't_{token}'
        g['tokens'] = (*g['tokens'], token)
        g[name] = get_pattern_function(name, pattern)

    return lex.lex()

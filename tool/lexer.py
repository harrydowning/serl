from types import FunctionType
import ply.lex as lex
import regex

# Define a couple of set functionality (e.g., switching lexing state) so arbitrary functions cannot be made
# def create_frule():
#     pass

def get_pattern_function(name, pattern):
    def f(t):
        s, e = t.lexer.lexmatch.span()
        string = t.lexer.lexmatch.string[s:e]
        m = regex.match(pattern, string, regex.VERBOSE)
        t.value = m.allcaptures()[1:]
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

    for token,  pattern in config.get('rules', []):
        token = token.upper()
        g['tokens'] = (*g['tokens'], token)
        g[f't_{token}'] = pattern

    for function_def in config.get('frules', []):
        exec(function_def)

    return lex.lex()

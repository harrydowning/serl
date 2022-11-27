import ply.lex as lex

# Define a couple of set functionality (e.g., switching lexing state) so arbitrary functions cannot be made
# def create_frule():
#     pass

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

def build_lexer(config: dict):
    g = globals()
    g['tokens'] = ()

    for token,  pattern in config.get('rules', []):
        token = token.upper()
        g['tokens'] = (*g['tokens'], token)
        g[f't_{token}'] = pattern

    for function_def in config.get('frules', []):
        exec(function_def)

    return lex.lex()

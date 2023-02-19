import tool.logger as logger
import ply.yacc as yacc

def get_prod_function(prod: tuple[str, str]):
    def f(p):
        pass
    
    f.__doc__ = f'{prod[0]} : {prod[1]}'
    return f

def p_error(p):
    print("Syntax error in input!") # TODO appropriate response

def build_parser(name: str, tokens: list[str], grammar: dict[str, list[str]]):
    g = globals()
    g['tokens'] = tokens

    for nt in grammar:
        for i, rule in enumerate(grammar[nt]):
            g[f'p_{nt}_{i}'] = get_prod_function((nt, rule))

    return yacc.yacc(debug=logger.debug, tabmodule=name)

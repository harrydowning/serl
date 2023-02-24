import os, itertools
import tool.logger as logger
import ply.yacc as yacc

def get_prod_function(prod: tuple[str, str], 
                      flipped_token_map: dict[str, str]):
    symbols = prod[1].split(' ')
    symbols = sorted([(s, i + 1) for i, s, in enumerate(symbols)])
    groups = {name: [i for _, i in group] for name, group in 
                       itertools.groupby(symbols, lambda x: x[0])}
    def f(p):
        p[0] = {
            flipped_token_map[symbol]: [p[i] for i in idxs] 
            for symbol, idxs in groups.items()
        }
    
    f.__doc__ = f'{prod[0]} : {prod[1]}'
    return f

def p_error(p):
    print("Syntax error in input!") # TODO appropriate response

def build_parser(tokens: list[str], token_map: dict[str, str],
                 grammar: dict[str, list[str]]):
    g = globals()
    g['tokens'] = tokens

    flipped_token_map = {v: k for k, v in token_map.items()}
    for nt in grammar:
        for i, rule in enumerate(grammar[nt]):
            g[f'p_{nt}_{i}'] = get_prod_function((nt, rule), flipped_token_map)

    filename = os.path.join(os.getcwd(), 'test.txt') # TODO temp
    return yacc.yacc(debug=logger.debug_mode, write_tables=False,
                     debuglog=logger.get_file_logger(filename), 
                     errorlog=logger)

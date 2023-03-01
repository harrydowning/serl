import os, itertools, re
import tool.logger as logger
import tool.utils as utils
from tool.config import TaggedData
import ply.yacc as yacc

def get_prod_function(prod: tuple[str, str], flipped_map: dict[str, str]):
    symbols = prod[1].split(' ')
    symbols = sorted([(s, i + 1) for i, s, in enumerate(symbols)])
    groups = {name: [i for _, i in group] for name, group in 
                       itertools.groupby(symbols, lambda x: x[0])}
    def f(p):
        p[0] = (prod[0], {
            flipped_map[symbol]: [p[i] for i in idxs] 
            for symbol, idxs in groups.items()
        })
    
    f.__doc__ = f'{prod[0]} : {prod[1]}'
    return f

def p_error(p):
    print("Syntax error in input!") # TODO appropriate response

def build_parser(tokens: list[str], symbol_map: dict[str, str],
                 grammar: dict[str, list[str]],
                 precedence: list[TaggedData]):
    g = globals()
    g['tokens'] = tokens
    g['precedence'] = [(tag, *tokens.split(' ')) for tag, tokens in precedence]

    flipped_map = {v: k for k, v in symbol_map.items()}
    for nt in grammar:
        for i, rule in enumerate(grammar[nt]):
            g[f'p_{nt}_{i}'] = get_prod_function((nt, rule), flipped_map)

    sorted_flipped_map = utils.get_sorted_map(flipped_map)
    filename = os.path.join(os.getcwd(), 'test.txt') # TODO temp
    file_logger = logger.get_file_logger(filename, sorted_flipped_map)
    return yacc.yacc(debug=logger.debug_mode, write_tables=False,
                     debuglog=file_logger, 
                     errorlog=logger.LoggerWrapper(sorted_flipped_map))

import os, itertools, re
import tool.logger as logger
import tool.utils as utils
from tool.config import TaggedData
import ply.yacc as yacc

class AST(tuple):
    def __new__(cls, name: str, pos: int, value, has_custom_value: bool):
        return super(AST, cls).__new__(cls, (name, pos, value))
    
    def __init__(self, name: str, pos: int, value, has_custom_value: bool) -> None:
        super().__init__()
        self.has_custom_value = has_custom_value

def get_prod_function(prod: tuple[str, int, str], flipped_map: dict[str, str]):
    symbols = prod[2].split(' ')
    symbols = sorted([(s, i + 1) for i, s, in enumerate(symbols)])
    groups = {name: [i for _, i in group] for name, group in 
                       itertools.groupby(symbols, lambda x: x[0])}
    def f(p):
        p[0] = AST(flipped_map(prod[0]), prod[1], {
            flipped_map[symbol]: [p[i] for i in idxs] 
            if len(idxs) > 1 else p[idxs[0]]
            for symbol, idxs in groups.items()
        }, False)
    
    f.__doc__ = f'{prod[0]} : {prod[2]}'
    return f

def p_error(p):
    if p != None:
        logger.error('Parsing error: Reached end of file.')
    else:
        tok = p.value[0][0] if type(p.value[0]) == list else p.value[0]
        logger.error(f'Parsing error: Token \'{tok}\' on line {p.lineno}')

def build_parser(_tokens: list[str], symbol_map: dict[str, str],
                 grammar: dict[str, list[str]], _precedence: list[TaggedData]):
    g = globals()
    g['tokens'] = _tokens
    
    precedence = []
    for tag, tok_str_list in _precedence:
        toks = []
        for t in re.split(r'\s+', tok_str_list):
            if symbol_map.get(t, None) != None:
                toks.append(symbol_map[t])
            else:
                logger.warning(f'precedence specified for token not used in '
                               f'grammar: \'{t}\'')
        if len(toks) > 0:
            precedence.append((tag, *toks))
    g['precedence'] = precedence

    flipped_map = {v: k for k, v in symbol_map.items()}
    for nt in grammar:
        for i, rule in enumerate(grammar[nt]):
            g[f'p_{nt}_{i}'] = get_prod_function((nt, i, rule), flipped_map)

    sorted_flipped_map = utils.get_sorted_map(flipped_map)
    filename = os.path.join(os.getcwd(), 'test.txt') # TODO temp
    file_logger = logger.get_file_logger(filename, sorted_flipped_map)
    return yacc.yacc(debug=logger.debug_mode, write_tables=False,
                     debuglog=file_logger, 
                     errorlog=logger.LoggingWrapper(sorted_flipped_map))

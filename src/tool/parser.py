import os, itertools, re
import tool.logger as logger
import tool.utils as utils
from tool.config import TaggedData
import ply.yacc as yacc

class AST(tuple):
    def __new__(cls, name: str, pos: int, value):
        return super(AST, cls).__new__(cls, (name, pos, value))

def get_prod_function(prod: tuple[str, int, str], flipped_map: dict[str, str]):
    symbols = prod[2].split(' ')
    symbols = sorted([(s, i + 1) for i, s, in enumerate(symbols)])
    groups = {name: [i for _, i in group] for name, group in 
                       itertools.groupby(symbols, lambda x: x[0])}
    def f(p):
        p[0] = AST(flipped_map[prod[0]], prod[1], {
            flipped_map[symbol]: [p[i] for i in idxs] 
            if len(idxs) > 1 else p[idxs[0]]
            for symbol, idxs in groups.items()
        })
    
    f.__doc__ = f'{prod[0]} : {prod[2]}'
    return f

def p_error(p):
    if p != None:
        logger.error('Parsing error: Reached end of file.')
    else:
        tok = p.value[0][0] if isinstance(p.value[0], list) else p.value[0]
        logger.error(f'Parsing error: Token \'{tok}\' on line {p.lineno}')

def build_parser(lang_name: str, _tokens: list[str], symbol_map: dict[str, str],
                 grammar: dict[str, list[str]], _precedence: list):
    g = globals()
    g['tokens'] = _tokens
    
    precedence = []
    for p in _precedence:
        if type(p) != TaggedData:
            logger.warning(f'Precedence rule \'{p}\' ignored as it has no '
                           f'associativity tag. Use \'!left\', \'!right\', or '
                           f'\'!nonassoc\'.')
            continue
        
        tag, tok_str_list = p
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

    flipped_map = utils.flip_map(symbol_map)
    for nt in grammar:
        for i, rule in enumerate(grammar[nt]):
            g[f'p_{nt}_{i}'] = get_prod_function((nt, i, rule), flipped_map)

    sorted_flipped_map = utils.get_sorted_map(flipped_map)
    filename = os.path.join(os.getcwd(), 'test.txt') # TODO temp

    debuglog = logger.get_file_logger(filename, sorted_flipped_map)
    errorlog = logger.LoggingWrapper(sorted_flipped_map, ply_repl=True)
    parser = yacc.yacc(debuglog=debuglog, errorlog=errorlog, write_tables=True, 
                       tabmodule=f'tabmodule_{lang_name}', debug=logger.debug_mode)
    g['parser'] = parser
    return parser

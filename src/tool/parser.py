import itertools, re, pathlib, os
import tool.logger as logger
import tool.utils as utils
import ply.yacc as yacc

class AST(tuple):
    def __new__(cls, name: str, pos: int, value):
        return super(AST, cls).__new__(cls, (name, pos, value))

def get_prod_func(prod: tuple[str, int, str], flipped_symbol_map: dict[str, str]):
    symbols = prod[2].split(' ')
    symbols = sorted([(s, i + 1) for i, s, in enumerate(symbols)])
    groups = {name: [i for _, i in group] for name, group in 
                       itertools.groupby(symbols, lambda x: x[0])}
    def f(p):
        p[0] = AST(
            flipped_symbol_map[prod[0]], 
            prod[1], 
            {flipped_symbol_map[symbol]: [p[i] for i in idxs] 
             if len(idxs) > 1 else p[idxs[0]]
             for symbol, idxs in groups.items()}
        )
    
    f.__doc__ = f'{prod[0]} : {prod[2]}'
    return f

def p_error(p):
    if p != None:
        logger.error('Parsing error: Reached end of file.')
    else:
        tok = p.value[0][0] if isinstance(p.value[0], list) else p.value[0]
        logger.error(f'Parsing error: Token \'{tok}\' on line {p.lineno}')

def build_parser(lang_name: str, _tokens: list[str], symbol_map: dict[str, str],
                 grammar: dict[str, list[str]], _precedence: list[str],
                 debug_file: str | None, sync: str, permissive: bool):
    g = globals()
    g['tokens'] = _tokens
    
    precedence = []
    for rule in _precedence:
        split = re.split(r'\s+', rule.strip())
        tag = split.pop(0)
        toks = [symbol_map[tok] for tok in split if symbol_map.get(tok, None)]
        if len(toks) > 0:
            precedence.append((tag, *toks))
    g['precedence'] = precedence

    flipped_symbol_map = utils.flip_dict(symbol_map)
    for nt in grammar:
        for i, rule in enumerate(grammar[nt]):
            g[f'p_{nt}_{i}'] = get_prod_func((nt, i, rule), flipped_symbol_map)

    sorted_flipped_symbol_map = utils.get_sorted_map(flipped_symbol_map)
    debug = bool(debug_file)
    tabmodule = f'tabmodule_{lang_name}'

    options = {
        'debug': debug,
        'tabmodule': tabmodule,
        'errorlog': logger.LoggingWrapper(repl_map=sorted_flipped_symbol_map, 
                                          ply_repl=True)
    }

    # Remove tables file (tabmodule) to regenerate debug file
    if debug:
        debuglog = logger.get_file_logger(debug_file, verbose=debug,
                                          repl_map=sorted_flipped_symbol_map)
        options['debuglog'] = debuglog
        package_dir = pathlib.Path(__file__).parent.resolve()
        try:
            os.remove(f'{os.path.join(package_dir, tabmodule)}.py')
        except OSError:
            pass

    parser = yacc.yacc(**options)
    
    if debug:
        exit(0)

    g['parser'] = parser
    return parser

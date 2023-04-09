import itertools
import re
import pathlib
import os
import inspect
import ctypes

import serl.logger as logger
import serl.utils as utils
from serl.lexer import get_whole_match

import ply.yacc as yacc

# parser = None
# symstack, statestack, state = [], [], 0
class SerlAST(tuple):
    def __new__(cls, name: str, pos: int, value):
        return super(SerlAST, cls).__new__(cls, (name, pos, value))

def get_prod_func(prod: tuple[str, int, str], flipped_symbol_map: dict[str, str]):
    symbols = prod[2].split(' ')
    symbols = sorted([(s, i + 1) for i, s, in enumerate(symbols)])
    groups = {name: [i for _, i in group] for name, group in 
                       itertools.groupby(symbols, lambda x: x[0])}
    def f(p):
        # global symstack, statestack, state
        # symstack, statestack, state = get_local_state()

        p[0] = SerlAST(
            flipped_symbol_map[prod[0]], 
            prod[1], 
            {
                flipped_symbol_map[symbol]: [p[i] for i in idxs] 
                for symbol, idxs in groups.items()
            }
        )
    
    f.__doc__ = f'{prod[0]} : {prod[2]}'
    return f

def get_error_msg(p, parser, flipped_symbol_map):
    expected = [
        'end of file' if symbol == '$end' else flipped_symbol_map[symbol] 
        for symbol in parser.action[parser.state].keys()
    ]
    
    if expected == []:
        expected_msg = ''
    else:
        s = '\' or \''
        expected_msg = f' Expected \'{s.join(expected)}\'.'

    if not p:
        return f'Parsing error: Reached end of file.{expected_msg}'

    tok = get_whole_match(p)
    tok_type = flipped_symbol_map[p.type]
    if tok == tok_type:
        tok_msg = f'Token \'{tok}\''
    else:
        tok_msg = f'Token \'{tok}\' of type \'{tok_type}\''
    
    return f'Parsing error: {tok_msg} on line {p.lineno}.{expected_msg}'

def update_local_state(state: int):
    frame = inspect.currentframe().f_back.f_back.f_back
    frame.f_locals['state'] = state
    ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame),ctypes.c_int(1))
    # print(frame.f_locals)

# def get_local_state():
#     frame = inspect.currentframe().f_back.f_back
#     statestack = frame.f_locals['statestack'].copy()
#     plen = frame.f_locals['plen']
#     del statestack[-plen:]
#     symstack = frame.f_locals['symstack'].copy()
#     sym = frame.f_locals['sym']
#     symstack.append(sym)
#     pname = frame.f_locals['pname']
#     goto = frame.f_locals['goto']
#     state = goto[statestack[-1]][pname]
#     statestack.append(state)
#     return symstack, statestack, state

def get_error_func(parser, sync, permissive, flipped_symbol_map):
    def error_func(p):
        logger.error(get_error_msg(p, parser, flipped_symbol_map))

        # if not p:
        #     print("End of File!")
        #     return

        # while True:
        #     tok = parser.token()
        #     if not tok or tok.type in sync: 
        #         break
        
        # parser.statestack.clear()
        # for s in statestack:
        #     parser.statestack.append(s)
        
        # parser.symstack.clear()
        # for sym in symstack:
        #     parser.symstack.append(sym)

        # update_local_state(state)

        # parser.errok()
    return error_func

def p_error(p):
    pass

def build_parser(lang_name: str, _tokens: list[str], symbol_map: dict[str, str],
                 grammar: dict[str, list[str]], _precedence: list[str],
                 debug_file: str | None, sync: str, permissive: bool):
    g = globals()
    g['tokens'] = _tokens
    
    precedence = []
    for rule in _precedence:
        split = re.split(r'\s+', rule.strip())
        tag = split.pop(0)
        toks = [symbol_map.get(tok, tok) for tok in split]# if symbol_map.get(tok, None)]
        if len(toks) > 0:
            precedence.append((tag, *toks))
    g['precedence'] = precedence

    flipped_symbol_map = utils.flip_dict(symbol_map)
    for nt in grammar:
        for i, rule in enumerate(grammar[nt]):
            g[f'p_{nt}_{i}'] = get_prod_func((nt, i, rule), flipped_symbol_map)

    sorted_flipped_symbol_map = utils.get_sorted_map(flipped_symbol_map)
    tabmodule = f'tabmodule_{utils.get_valid_identifier(lang_name)}'

    options = {
        'debug': True,
        'tabmodule': tabmodule,
        'errorlog': logger.LoggingWrapper(repl_map=sorted_flipped_symbol_map, 
                                          ply_repl=True)
    }

    # Remove tables file (tabmodule) to regenerate debug file
    debug_parser = bool(debug_file)
    if debug_parser:
        debuglog = logger.get_file_logger(debug_file, verbose=debug_parser,
                                          repl_map=sorted_flipped_symbol_map)
        options['debuglog'] = debuglog
        package_dir = pathlib.Path(__file__).parent.resolve()
        try:
            os.remove(f'{os.path.join(package_dir, tabmodule)}.py')
        except OSError:
            pass

    parser = yacc.yacc(**options)

    sync = [] if not sync else re.split(r'\s+', sync.strip())
    sync = [symbol_map.get(symbol, symbol) for symbol in sync]
    error_func = get_error_func(parser, sync, permissive, flipped_symbol_map)
    parser.errorfunc = error_func
    g['parser'] = parser
    
    if debug_parser:
        exit(0)

    return parser

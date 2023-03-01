import sys, os, fileinput
from docopt import docopt
import networkx as nx
from tool.lexer import build_lexer
from tool.parser import build_parser
import tool.utils as utils
import tool.logger as logger
from tool.constants import CLI, SYMLINK_CLI, NAME, VERSION, DEFAULT_REF
from tool.config import get_config

# def default_old(args):
#     language = args['<language>'] # Also check 0th arg for symlink
#     src = args['<input>']
#     strict_mode = args['--strict']
#     debug_mode = args['--debug']

#     # system_config = get_system_config(SYSTEM_CONFIG_FILE)
#     # path_config = get_path_config(args['--config'])

#     local_config = {} #utils.get_local_config(LOCAL_CONFIG_FILE)[language]
#     rules = utils.get_sorted_rules(local_config['rules'])
#     tokens = local_config['tokens']

#     rule_graph = nx.DiGraph(utils.get_rule_graph(rules))
#     cycles = list(nx.simple_cycles(rule_graph))

#     if cycles:
#         cycle_nodes = {node for cycle in cycles for node in cycle}
#         rule_graph.remove_nodes_from(cycle_nodes)

#         for cycle in cycles:
#             msg = (f"Cyclic reference in rules: '{', '.join(cycle)}'."
#                     " Rules will not be expanded. This is most likely not" 
#                     " indended, please check rules.")
#             # logger.warning(msg, strict_mode)

#     rule_order = list(nx.topological_sort(rule_graph))
#     rules = utils.expand_rules(rule_order, rules)

#     syntax = utils.expand_patterns(tokens, rules)
#     lexer = build_lexer(syntax, args['--debug'])

#     with open(src) as file:
#         src_str = file.read()
#         # TODO: inline_config 

#     code = local_config['code'] # make keys upper to match tokens
#     env = {
#         'src': src
#     }
#     _setup = code['setup']
#     exec(_setup, env)

#     lexer.input(src_str)
#     # logger.info(' ==== TOKENS FOLLOW ====', debug_mode)
#     for token in lexer:
#         # logger.info(token, debug_mode)
#         env['captures'] = token.value
#         _token_code = code[token.type.lower()]
#         exec(_token_code, env)

#     _result = code['result']
#     exec(_result, env)

def token_expansion(tokens: dict[str, str], split: list[str]) -> dict[str, str]:
    repl_tokens = utils.get_repl_tokens(tokens, split)
    token_graph = nx.DiGraph(utils.get_token_graph(repl_tokens))
    cycles = list(nx.simple_cycles(token_graph))

    if cycles:
        cycle_nodes = {node for cycle in cycles for node in cycle}
        token_graph.remove_nodes_from(cycle_nodes)
        token_map = dict(zip(repl_tokens.keys(), tokens.keys()))
        
        for i, cycle in enumerate(cycles):
            cycle = map(lambda tok: f'\'{token_map[tok]}\'', cycle)
            msg = (f'Cyclic reference involving {", ".join(cycle)}.'
                    ' Preceding token(s) will not be expanded.')
            logger.warning(msg)
            
            shown = i + 1 
            remaining = len(cycles) - shown
            if shown >= len(tokens) and remaining > 1:
                logger.warning(f'[{remaining} more cycles...]')
                break

    exp_order = list(nx.topological_sort(token_graph))
    exp_tokens = utils.expand_tokens(exp_order, repl_tokens)
    return dict(zip(tokens.keys(), exp_tokens.values()))

def extension(file: str) -> str:
    if os.name == 'nt':
        file += '.exe'
    return file

def requirements(req_file: str, reqs: str) -> None:
    if reqs == '':
        logger.warning('No requirements specified.')
    
    with open(req_file, 'w') as file:
        file.write(reqs)
    
    exit(0)

def link(args):
    # TODO Check <language> exists in .tool and not a path?
    language = args['<language>'].split('.')[0]
    dir = args['<dir>'] or os.getcwd()
    
    src = extension(sys.argv[0])
    dst = extension(os.path.join(dir, f'{language}'))
    
    try:
        os.symlink(src, dst)
    except Exception as e:
        logger.error(e)

def default(args):
    language = args['<language>']
    config = get_config(language)

    req_file = args['--requirements']
    if req_file:
        requirements(req_file, config.get('requirements', ''))

    version = config.get('version', None)
    usage = config.get('usage', None)
    
    inputs = args['<input>']

    # User language docopt
    if usage != None:
        language_args = docopt(usage, argv=inputs, version=version)
        # Requirement: Must specify single <input> in usage to be file parsed.
        src_input = language_args['<input>']
    else:
        src_input = next(iter(inputs), None) # First element if it exists
    
    # Read input file if prsent else read from stdin
    with fileinput.input(files=src_input or ()) as file:
        src = ''.join(file)
    
    meta = config.get('meta', {})
    meta_tokens = meta.get('tokens', {})

    tokens = config['tokens']
    ignore_tok = tokens.pop('_ignore', ' \t') # Special token, not expanded
    
    ref = meta_tokens.get('ref', DEFAULT_REF)
    if ref != False:
        # if 'token' not used assume given string is prefix of token repl.
        ref += '' if 'token' in ref else 'token'
        logger.info(f'Performing token expansion with \'ref\' pattern '
                    f'\'{ref}\' (default: \'{DEFAULT_REF}\')')
        tokens = token_expansion(tokens, ref.split('token'))
    
    logger.info('===== TOKENS =====')
    for token, pattern in tokens.items():
        logger.info(f'{token}: \'{pattern.strip()}\'')
    logger.info('===== TOKENS =====')

    grammar = config['grammar']
    token_map = {k: f'TERM{i}' for i, k, in enumerate(tokens.keys())}
    grammar_map = {k: f'NONTERM{i}' for i, k in enumerate(grammar.keys())}
    common_keys = set(token_map.keys()).intersection(grammar_map.keys())
    if common_keys:
        s = "\', \'"
        logger.error(f'Grammar identifiers \'{s.join(common_keys)}\' already '
                     f'used in tokens')
    
    symbol_map = token_map | grammar_map
    grammar = utils.normalise_grammar(symbol_map, grammar)

    tokens_in_grammar = utils.get_tokens_in_grammar(token_map, grammar)
    tokens = {k: v for k, v in tokens.items() if k in tokens_in_grammar}
    token_map = {k: v for k, v in token_map.items() if k in tokens_in_grammar}
    symbol_map = token_map | grammar_map

    lexer = build_lexer(tokens, token_map, ignore_tok, 
                        meta_tokens.get('regex', False))
    parser = build_parser(list(token_map.values()), symbol_map, grammar, 
                          config.get('precedence', []))
    # ast = parser.parse(src, lexer=lexer)
    # code = config['code']
    # execute(ast, code)

def execute(ast, code: dict):
    pass # TODO language execution

def get_args() -> dict:
    version = f'{NAME} {VERSION}'
    command = extension(sys.argv[0])
    if os.path.islink(command):
        # Stop initial args acting on the tool and not the language
        if not '--' in sys.argv:
            sys.argv.insert(1, '--')
        args = docopt(SYMLINK_CLI, version=version, options_first=True)
        base = os.path.basename(command)
        args['<language>'] = base.split('.')[0]
    else:
        args = docopt(CLI, version=version, options_first=True)
    return args

def main():
    args = get_args()
    logger.debug_mode = args.get('--debug', False)
    logger.strict_mode = args.get('--strict', False)

    if args.get('link', False):
        link(args)
    else:
        default(args)


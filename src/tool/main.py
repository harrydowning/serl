import sys, os, fileinput
from docopt import docopt
from tool.lexer import build_lexer
from tool.parser import build_parser
import tool.utils as utils
import tool.logger as logger
from tool.constants import CLI, SYMLINK_CLI, NAME, VERSION
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

def requirements(reqs: str) -> None:
    file = 'requirements.txt'
    if reqs == '':
        logger.warning('No requirements specified.')
    
    if os.path.exists(file):
        question = 'File "requirements.txt" alread exists, overwrite?'
        overwrite = logger.confirm(question)
        if not overwrite:
            exit(0)
    
    with open(file, 'w') as file:
        file.write(reqs)
    exit(0)

def link(args):
    # TODO Check <language> exists in .tool and not a path?
    language = args['<language>'].split('.')[0]
    dir = args['<dir>'] or os.getcwd()
    
    src = os.path.abspath(__file__)
    dst = os.path.join(dir, f'{language}')
    
    if os.name == 'nt':
        dst += '.exe'
    
    try:
        os.symlink(src, dst)
    except Exception as e:
        logger.error(e)

def default(args):
    language = args['<language>']
    config = get_config(language)

    if args['--requirements']:
        requirements(config.get('requirements', ''))

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
    
    ref = meta_tokens.get('ref', '^token(?!$)| token')
    if ref != False:
        # if 'token' not used assume given string is prefix of token repl.
        ref += '' if 'token' in ref else 'token'
        tokens = utils.token_expansion(tokens, ref.split('token'))
    
    logger.announce('TOKENS', [f'{token}: \'{pattern}\'' 
                               for token, pattern in tokens.items()])
    # TODO filter_tokens to remove those not in grammar
    lexer, token_map = build_lexer(tokens, ignore_tok)
    grammar = utils.normalise_grammar(token_map, config['grammar'])
    utils.check_undefined(token_map, grammar)
    
    # parser = build_parser(language, list(token_map.values()), grammar) # TODO language name may not be unique
    # ast = parser.parse(src, lexer=lexer)
    # code = config['code']
    # execute(ast, code)

def execute(ast, code: dict):
    pass # TODO language execution

def get_args() -> dict:
    version = f'{NAME} {VERSION}'
    command = sys.argv[0]
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
    logger.debug = args.get('--debug', False)
    logger.strict = args.get('--strict', False)

    if args.get('link', False):
        link(args)
    else:
        default(args)


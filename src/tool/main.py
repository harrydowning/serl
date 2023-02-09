import os, fileinput
from docopt import docopt
import networkx as nx
from tool.lexer import build_lexer
import tool.utils as utils
import tool.logger as logger
from tool.constants import CLI, NAME, VERSION
from tool.config import get_config

def default_old(args):
    language = args['<language>'] # Also check 0th arg for symlink
    src = args['<input>']
    strict_mode = args['--strict']
    debug_mode = args['--debug']

    # system_config = get_system_config(SYSTEM_CONFIG_FILE)
    # path_config = get_path_config(args['--config'])

    local_config = {} #utils.get_local_config(LOCAL_CONFIG_FILE)[language]
    rules = utils.get_sorted_rules(local_config['rules'])
    tokens = local_config['tokens']

    rule_graph = nx.DiGraph(utils.get_rule_graph(rules))
    cycles = list(nx.simple_cycles(rule_graph))

    if cycles:
        cycle_nodes = {node for cycle in cycles for node in cycle}
        rule_graph.remove_nodes_from(cycle_nodes)

        for cycle in cycles:
            msg = (f"Cyclic reference in rules: '{', '.join(cycle)}'."
                    " Rules will not be expanded. This is most likely not" 
                    " indended, please check rules.")
            logger.warning(msg, strict_mode)

    rule_order = list(nx.topological_sort(rule_graph))
    rules = utils.expand_rules(rule_order, rules)

    syntax = utils.expand_patterns(tokens, rules)
    lexer = build_lexer(syntax, args['--debug'])

    with open(src) as file:
        src_str = file.read()
        # TODO: inline_config 

    code = local_config['code'] # make keys upper to match tokens
    env = {
        'src': src
    }
    _setup = code['setup']
    exec(_setup, env)

    lexer.input(src_str)
    logger.info(' ==== TOKENS FOLLOW ====', debug_mode)
    for token in lexer:
        logger.info(token, debug_mode)
        env['captures'] = token.value
        _token_code = code[token.type.lower()]
        exec(_token_code, env)

    _result = code['result']
    exec(_result, env)

def link(args):
    language = args['<language>'].split('.')[0]
    dir = args['<dir>'] or os.getcwd()
    
    src = os.path.abspath(__file__)
    dst = os.path.join(dir, f'{language}')
    
    if os.name == 'nt':
        dst += '.exe'
    
    os.symlink(src, dst)

def default(args):
    language = args['<language>']
    config = get_config(language)

    version = config.get('version', None)
    usage = config.get('usage', None)

    inputs = args['<input>']

    # User language docopt
    if usage != None:
        language_argv = [language, *inputs]
        language_args = docopt(usage, argv=language_argv, version=version)
        # Requirement: Must specify single <input> in usage to be file parsed.
        src_input = language_args['<input>']
    else:
        src_input = next(iter(inputs), None) # First element if it exists
    
    # Read input file if prsent else read from stdin
    with fileinput.input(files=src_input or ()) as file:
        src = ''.join(file)
    print(src)
    
def main():
    args = docopt(CLI, version=f'{NAME} {VERSION}')
    if args['link']:
        link(args)
    else:
        default(args)


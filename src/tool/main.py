import os, logging
from docopt import docopt
import networkx as nx
from tool.lexer import build_lexer
import tool.utils as utils

# TODO: Potentially use configparser
NAME = 'tool'
VERSION = '0.0.1'
SYSTEM_CONFIG_FILE = f'.{NAME}rc'
LOCAL_CONFIG_FILE = f'config.yaml'

CLI = f"""{NAME}

Usage:
  {NAME} link [-d] <language>
  {NAME} [options] <language> <src>

Options:
  -h --help               Show this screen.
  -v --version            Show version.
  -c --config=PATH        Specify a path to another config file to add to the 
                          overall config. Config precedence is as follows: 
                          system (lowest), path, local, inline (highest). 
  --debug                 Run in debug mode. This displays the master regex
                          construction.
  --strict                Run in strict mode. This stops evaluation at the
                          first warning.
"""

def setup():
    logging.basicConfig(format='%(levelname)s:%(message)s')
    logging.getLogger().setLevel(logging.INFO)

def warning(message, strict_mode):
    logging.warning(message)
    if strict_mode:
        exit(1)

def info(message, debug_mode):
    if debug_mode:
        logging.info(message)

def link(args):
    language = args['<language>']
    delete = args['-d']
    
    if delete:
        pass

    src = os.path.abspath(__file__)
    dst = os.path.join(os.getcwd(), f'{language}')
    if os.name == 'nt':
        dst += '.exe'

    #os.symlink(src, dst)


def default(args):
    language = args['<language>'] # Also check 0th arg for symlink
    src = args['<src>']
    strict_mode = args['--strict']
    debug_mode = args['--debug']

    # system_config = get_system_config(SYSTEM_CONFIG_FILE)
    # path_config = get_path_config(args['--config'])

    local_config = utils.get_local_config(LOCAL_CONFIG_FILE)[language]
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
            warning(msg, strict_mode)

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
    info(' ==== TOKENS FOLLOW ====', debug_mode)
    for token in lexer:
        info(token, debug_mode)
        env['captures'] = token.value
        _token_code = code[token.type.lower()]
        exec(_token_code, env)

    _result = code['result']
    exec(_result, env)


def main():
    setup()
    args = docopt(CLI, version=f'{NAME} {VERSION}')
    if args['link']:
        link(args)
    else:
        default(args)


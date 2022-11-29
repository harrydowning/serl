import sys
from docopt import docopt
import networkx as nx
from tool.lexer import build_lexer
import tool.utils as utils

# Potentially use configparser
NAME = 'tool'
VERSION = '0.0.1'
SYSTEM_CONFIG_FILE = f'.{NAME}rc'
LOCAL_CONFIG_FILE = f'config.yaml'

CLI = f"""{NAME}

Usage:
  {NAME} [options] <language> <src>
  {NAME} link [-d] <language>

Options:
  -h --help               Show this screen.
  -v --version            Show version.
  -c --config=PATH        Specify a path to another config file to add to the 
                          overall config. Config precedence is as follows: 
                          system (lowest), path, local, inline (highest). 
  -l --language=LANGUAGE  Specify the name of the language to use from the 
                          config.
  --debug                 Run in debug mode. This displays the master regex
                          construction.
  --strict                Run in strict mode. This stops evaluation at the
                          first warning.
"""

def main():
    args = docopt(CLI, version=f'{NAME} {VERSION}')
    language = args['<language>'] # Also check 0th arg for symlink
    src = args['<src>']

    # system_config = get_system_config(SYSTEM_CONFIG_FILE)
    # path_config = get_path_config(args['--config'])

    local_config = utils.get_local_config(LOCAL_CONFIG_FILE)[language]
    rules = utils.get_sorted_rules(local_config['rules'])
    block = local_config['block']

    v, e = utils.get_rule_graph(rules)
    G = nx.DiGraph(e)
    cycles = list(nx.simple_cycles(G))

    if cycles:
        cycle_nodes = {n for l in cycles for n in l}
        G.remove_nodes_from(cycle_nodes)
        # TODO: warnings own module (and includ strict mode logic)
        for node in cycle_nodes:
            print(f"[Warning]: Cycle detected involving rule '{node}'. Rule not expanded any further. This is most likely not indended, check rule.", file=sys.stderr)

    rule_order = list(nx.topological_sort(G))
    rules = utils.expand_rules(rule_order, rules)

    syntax = utils.expand_patterns(block, rules)
    lexer = build_lexer(syntax, args['--debug'])

    with open(src) as file:
        src_str = file.read()
        # TODO: inline_config 

    lexer.input(src_str)
    for token in lexer:
        print(token)
    
    



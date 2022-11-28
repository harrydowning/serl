
from docopt import docopt
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
  -c --config=CONFIG      Specify a file to partially or completely override 
                          the system config.
  -l --language=LANGUAGE  Specify the name of the language to use from the 
                          system config.
"""

def main():
    args = docopt(CLI, version=f'{NAME} {VERSION}')
    language = args['<language>'] # Also check 0th arg for symlink
    src = args['<src>']

    # system_config = get_system_config(SYSTEM_CONFIG_FILE)
    # path_config = get_path_config(args['--config'])

    local_config = utils.get_local_config(LOCAL_CONFIG_FILE)[language]
    rules = local_config['rules']
    block = local_config['block']

    rules = utils.expand_patterns(rules, rules)
    syntax = utils.expand_patterns(block, rules)
    lexer = build_lexer(syntax)
    
    print(syntax)

    with open(src) as file:
        src_str = file.read()
        # TODO: inline_config 

    lexer.input(src_str)
    for token in lexer:
        print(token)
    
    



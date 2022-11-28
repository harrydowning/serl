import os, io, pathlib
import yaml
from docopt import docopt
from lexer import build_lexer

# Potentially use configparser
NAME = 'tool'
VERSION = '0.0.1'
SYSTEM_CONFIG_FILE = f'.{NAME}rc'
LOCAL_CONFIG_FILE = f'config.yaml'

CLI = f"""{NAME}

Usage:
  {NAME} [options] <src>
  {NAME} link [-d] <language>

Options:
  -h --help               Show this screen.
  -v --version            Show version.
  -c --config=CONFIG      Specify a file to partially or completely override 
                          the system config.
  -l --language=LANGUAGE  Specify the name of the language to use from the 
                          system config.
"""

def yaml_load_all(file: io.TextIOWrapper) -> dict:
    config = {}
    for i, doc in enumerate(yaml.safe_load_all(file)):
        if type(doc) != dict:
            continue
        # Note: If a language is named with an index it could be overriden
        name = doc.get('name', i)
        config[name] = doc
    return config

def get_system_config() -> dict:
    home = os.path.expanduser('~')
    
    try:
        with open(os.path.join(home, SYSTEM_CONFIG_FILE)) as file:
            system_config = yaml_load_all(file)
    except FileNotFoundError:
        system_config = {}
    
    return system_config

def get_path_config(path: str | None) -> dict:
    if path == None:
        return {}
    
    # Note: may want this error to be shown to users
    try:
        with open(path) as file:
            path_config = yaml_load_all(file)
    except FileNotFoundError:
        path_config = {}

    return path_config

def get_local_config() -> dict:
    local_path = None
    
    for path in pathlib.Path().rglob(LOCAL_CONFIG_FILE):
        local_path = path
        break
    
    if local_path == None:
        return {}

    with open(local_path) as file:
        path_config = yaml_load_all(file)

    return path_config

# def get_inline_config(src: str) -> tuple[dict, str]:
#     with open(src) as file:
#         inline_config, content = list(yaml.safe_load_all(file))[:2]
#     return inline_config, content

def main():
    args = docopt(CLI, version=f'{NAME} {VERSION}')
    # system_config = get_system_config()
    # path_config = get_path_config(args['--config'])
    local_config = get_local_config()
    print(local_config)
    # inline_config = 


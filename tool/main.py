import os
import yaml
import docopt

# Potentially use configparser
_NAME = 'tool'
_VERSION = '0.0.1'
_SYSTEM_CONFIG_FILE = f'.{_NAME}rc'
_LOCAL_CONFIG_FILE = f'.rc'

_CLI = f"""{_NAME}

Usage:
  {_NAME} [options] <src>

Options:
  -h --help               Show this screen.
  -v --version            Show version.
  -c --config=CONFIG      Specify a file to partially or completely override 
                          the system config.
  -l --language=LANGUAGE  Specify the name of the language to use from the 
                          system config.
  -s --symlink            Create a symbolic link of the current language
"""

_is_using_cli = False

def _get_system_config() -> dict:
    home = os.path.expanduser('~')
    
    with open(os.path.join(home, _SYSTEM_CONFIG_FILE)) as file:
        system_config = {}
        for doc in yaml.safe_load_all(file):
            system_config[doc['name']] = doc
    
    return system_config

def _get_path_config(path: str | None) -> dict:
    if path == None:
        return {}

    with open(path) as file:
        path_config = yaml.safe_load(file)
    
    return path_config

def _get_local_config() -> dict:
    if path == None:
        return {}

    with open(path) as file:
        path_config = yaml.safe_load(file)
    
    return path_config

def main():
    global _is_using_cli 
    _is_using_cli = True

    args = docopt(_CLI, version=f'{_NAME} {_VERSION}')

    system_config = _get_system_config()
    path_config = _get_path_config(args['--config'])


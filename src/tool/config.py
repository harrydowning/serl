import os, sys, re
import yaml
import requests
import tool.logger as logger
from tool.constants import SYSTEM_CONFIG_DIR
from tool.schema import validate

class TaggedData(tuple):
    def __new__(cls, tag: str, value):
        return super(TaggedData, cls).__new__(cls, (tag, value))

def tagger(loader: yaml.Loader, tag_suffix, node):
    match type(node):
        case yaml.nodes.ScalarNode:
            val = loader.construct_scalar(node)
        case yaml.nodes.MappingNode:
            val = loader.construct_mapping(node)
        case yaml.nodes.SequenceNode:
            val = loader.construct_sequence(node)
    return TaggedData(tag_suffix, val)

yaml.add_multi_constructor('!', tagger, Loader=yaml.SafeLoader)

class LanguageName(str):
    def lang_name(self):
        return os.path.basename(self).split('.')[0]

def get_home_dir() -> str:
    home = os.path.expanduser('~')
    return os.path.join(home, SYSTEM_CONFIG_DIR)

def get_system_config_text(language: LanguageName) -> str | None:
    home_dir = get_home_dir()
    # Allow Python files with functionality to be shared across languages
    sys.path.append(home_dir)
    
    for filename in os.listdir(home_dir):
        file_lang = filename.split('.')[0]
        file_path = os.path.join(home_dir, filename)

        if filename == language or file_lang == language:
            with open(file_path) as file:
                return file.read()
    return None

def get_file_config_text(language: LanguageName) -> str | None:
    try:
        with open(language) as file:
            return file.read()
    except FileNotFoundError:
        return None

def get_url_config_text(url: str) -> str | None:
    r = requests.get(url)
    r.raise_for_status()
    return r.text

def get_config_text(language: LanguageName) -> str | None:
    if re.match(r'https?://.*', language):
        try:
            config_text = get_url_config_text(language)
        except requests.exceptions.ConnectionError as ce:
            logger.error(ce)
        except requests.exceptions.HTTPError as httpe:
            logger.error(httpe)
        except requests.exceptions.RequestException as rqe:
            logger.error(rqe)
    else:
        # File config has higher precedence than system
        config_text = get_file_config_text(language) or get_system_config_text(language)
        if config_text == None:
            logger.error(f"Could not find system or file config for " 
                         f"\'{language}\'.")
    return config_text

def get_config(language: LanguageName) -> dict:
    config_text = get_config_text(language)
    config = yaml.safe_load(config_text)

    valid, error = validate(config)
    if valid:
        return config
    else:
        logger.error(f'Validation error in config \'{language}\'. {error}')

def install(language: LanguageName, alias: str | None):
    alias = alias or language.lang_name()
    config_text = get_config_text(language)
    home_dir = get_home_dir()
    filename = os.path.join(home_dir, f'{alias}.yaml')
    
    if os.path.isfile(filename):
        logger.error(f'Language \'{alias}\' already exists.')
    
    with open(filename, 'w') as file:
        file.write(config_text)
    print(f'Successfully installed {alias}.')

def uninstall(language: LanguageName):
    lang_name = language.lang_name()
    home_dir = get_home_dir()
    for filename in os.listdir(home_dir):
        file_lang = filename.split('.')[0]
        file_path = os.path.join(home_dir, filename)

        if filename == language or file_lang == language:
            os.remove(file_path)
            print(f'Successfully uninstalled {lang_name}.')
            return
    logger.warning(f'Skipping, {lang_name} not already installed.')
import os, sys, re
import yaml
import requests
import tool.logger as logger
from tool.constants import SYSTEM_CONFIG_DIR
from tool.schema import validate

def get_home_dir() -> str:
    home = os.path.expanduser('~')
    home_dir = os.path.join(home, SYSTEM_CONFIG_DIR)
    os.makedirs(home_dir, exist_ok=True)
    return home_dir

def get_system_config_text(language: str) -> str | None:
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

def get_file_config_text(language: str) -> str | None:
    try:
        with open(language) as file:
            return file.read()
    except FileNotFoundError:
        return None

def get_url_config_text(url: str) -> str | None:
    r = requests.get(url)
    r.raise_for_status()
    return r.text

def get_config_text(language: str) -> str | None:
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

def get_config(language: str) -> dict:
    config_text = get_config_text(language)
    config = yaml.safe_load(config_text) # TODO handle errors

    valid, error = validate(config)
    if valid:
        return config
    else:
        logger.error(f'Validation error in config \'{language}\'. {error}')

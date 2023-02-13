import os, re
import yaml
import requests
from tool.logger import Logger
from tool.constants import SYSTEM_CONFIG_DIR
from tool.schema import validate

def get_system_config(language: str) -> dict:
    home = os.path.expanduser('~')
    directory = os.path.join(home, SYSTEM_CONFIG_DIR)
    config = {}
    
    for filename in os.listdir(directory):
        file_lang = file.split(".")[0]
        file_path = os.path.join(directory, filename)

        if filename == language or file_lang == language:
            with open(file_path) as file:
                config = yaml.safe_load(file)
            break

    return config

def get_file_config(file_path: str) -> dict:
    try:
        with open(file_path) as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        config = {}
    return config

def get_url_config(url: str) -> dict:
    r = requests.get(url)
    r.raise_for_status()
    return yaml.safe_load(r.text)

def get_config(language: str, logger: Logger) -> dict:
    if re.match(r'https?://.*', language):
        try:
            config = get_url_config(language)
        except requests.exceptions.ConnectionError as ce:
            logger.error(ce)
        except requests.exceptions.HTTPError as httpe:
            logger.error(httpe)
        except requests.exceptions.RequestException as rqe:
            logger.error(rqe)
    else:
        # File config has higher precedence than system
        config = get_file_config(language) or get_system_config(language)
        if config == {}:
            logger.error(f"Could not find system or file config for language: " 
                         f"{language}.")

    valid, message = validate(config)
    if valid:
        return config
    else:
        logger.error(message)

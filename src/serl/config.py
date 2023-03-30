import os, re
import yaml
import requests
import serl.logger as logger
from serl.constants import SYSTEM_CONFIG_DIR, SYSTEM_CONFIG_ENV_DIR
from serl.schema import validate

def get_config_dir(path=[]) -> str:
    home = os.path.expanduser('~')
    config_dir = os.path.join(home, SYSTEM_CONFIG_DIR, *path)
    os.makedirs(config_dir, exist_ok=True)
    return config_dir

def get_config_env_dir() -> str:
    return get_config_dir([SYSTEM_CONFIG_ENV_DIR])

def system_config_languages() -> list[str]:
    config_dir = get_config_dir()
    return [filename for filename in os.listdir(config_dir) 
            if not os.path.isdir(os.path.join(config_dir, filename))]

def system_config_exists(language: str):
    return language in system_config_languages()

def get_file_config_text(language: str, prefix: str ='') -> str | None:
    path = os.path.join(prefix, language)
    try:
        with open(path) as file:
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
        config_text = get_file_config_text(language) or \
            get_file_config_text(language, get_config_dir())
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

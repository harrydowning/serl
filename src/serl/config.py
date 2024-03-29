import os
import re

import serl.logger as logger
from serl.constants import SYSTEM_CONFIG_DIR, SYSTEM_CONFIG_ENV_DIR
from serl.schema import validate

import yaml
import requests

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

def get_config_text(language: str, symlink: bool) -> str | None:
    if re.match(r'https?://.*', language):
        try:
            config_text = get_url_config_text(language)
        except requests.exceptions.ConnectionError as ce:
            logger.error(ce, code=1)
        except requests.exceptions.HTTPError as httpe:
            logger.error(httpe, code=1)
        except requests.exceptions.RequestException as rqe:
            logger.error(rqe, code=1)
    else:
        config_text = None
        if not symlink:
            # File config has higher precedence than system
            config_text = get_file_config_text(language)
        config_text = config_text or \
            get_file_config_text(language, get_config_dir())
        if config_text == None:
            logger.error(f"Could not find system or file config for " 
                         f"\'{language}\'.", code=1)
    return config_text

def get_config(language: str, symlink: bool) -> dict:
    config_text = get_config_text(language, symlink)
    try:
        config = yaml.safe_load(config_text)
    except yaml.YAMLError as err:
        err.with_traceback(None)
        logger.error(f'YAML parser error:\n\n{err}', code=1)

    errs = validate(config)
    if errs == []:
        return config
    else:
        err_msg = lambda file, err: f'Validation error in \'{file}\': {err}'
        last = errs.pop()
        for err in errs:
            logger.error(err_msg(language, err))
        logger.error(err_msg(language, last), code=1) 

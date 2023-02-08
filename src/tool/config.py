import os, re
import yaml
import requests
from tool.constants import SYSTEM_CONFIG_DIR

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

    if config == {}:
        err_msg = f"No system config for language {language} found."
        raise FileNotFoundError(err_msg)

    return config

def get_file_config(file_path: str) -> dict:
    config = {}
    with open(file_path) as file:
        config = yaml.safe_load(file)
    return config

def get_url_config(url: str) -> dict:
    r = requests.get(url)
    return yaml.safe_load(r.text)

def get_config(language: str) -> dict:
    pass
    # try:
    #     if re.match(r'https?://.*', language):
    #         config = get_url_config(language)
    #     else:
    #         try:
    #             config = get_file_config
    #         except FileNotFoundError:
    #             config
                
        

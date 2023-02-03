import logging

# Setup
logging.basicConfig(format='%(levelname)s:%(message)s')
logging.getLogger().setLevel(logging.INFO)

def warning(message, strict_mode):
    logging.warning(message)
    if strict_mode:
        exit(1)

def info(message, debug_mode):
    if debug_mode:
        logging.info(message)
import logging

debug_mode = False
strict_mode = False

logging.basicConfig(format='%(levelname)s: %(message)s')
logging.getLogger().setLevel(logging.INFO)

def info(msg, *args):
    if debug_mode:
        logging.info(msg, *args)

def debug(*args):
     info(*args)

def announce(title: str, messages: list[str]):
    info(f'===== {title.upper()} =====')
    for message in messages:
          info(message)
    info(f'===== {title.upper()} =====')

def confirm(question, positive=['y'], negative=['n']):
    prompt = f'{question} [{"".join(positive)}/{"".join(negative)}] '
    ans = ""
    while not ans in positive + negative:     
        ans = input(prompt).strip()
        if ans in positive + negative:
            break
    return ans in positive

def warning(msg, *args):
        logging.warning(msg, *args)
        if strict_mode:
            exit(1)

def error(msg, *args):
    logging.error(msg, *args)
    exit(1)
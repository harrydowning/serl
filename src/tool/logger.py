import logging

debug = False
strict = False

logging.basicConfig(format='%(levelname)s: %(message)s')
logging.getLogger().setLevel(logging.INFO)

def info(message):
    if debug:
        logging.info(message)

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

def warning(message):
        logging.warning(message)
        if strict:
            exit(1)

def error(message):
    logging.error(message)
    exit(1)
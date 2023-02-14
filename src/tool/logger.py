import logging

class Logger:
    def __init__(self, debug, strict):
        logging.basicConfig(format='%(levelname)s: %(message)s')
        logging.getLogger().setLevel(logging.INFO)
        self.debug = debug
        self.strict = strict

    def info(self, message):
        if self.debug:
            logging.info(message)
    
    def confirm(self, question, positive=['y'], negative=['n']):
        prompt = f'{question} [{"".join(positive)}/{"".join(negative)}] '
        ans = ""
        while not ans in positive + negative:     
            ans = input(prompt).strip()
            if ans in positive + negative:
                break
        return ans in positive

    def warning(self, message):
        logging.warning(message)
        if self.strict_mode:
            exit(1)

    def error(self, message):
        logging.error(message)
        exit(1)
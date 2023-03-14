import re
import tool.logger as logger
from tool.utils import Grammar
import pygments
from pygments.style import Style
from pygments.util import ClassNotFound
from pygments.lexer import RegexLexer
from pygments.token import string_to_tokentype
from pygments.formatters import get_formatter_by_name

class PygmentsLexer(RegexLexer):
    flags = [re.VERBOSE]
    # TODO ignore tokens in each state
    # TODO states represent grammar non terminals
    # string_to_tokentype(token_type.title()) # TODO token_type str of the form '<name>.<name>...'

class PygmentsStyle(Style):
    def __init__(self, grammar: Grammar) -> None:
        super().__init__()
        self.styles = {string_to_tokentype(token_type): style 
                       for token_type, style in grammar.style}

def get_pygment_output(code: str, grammar: Grammar, format: str) -> str:
    # TODO use grammar to create lexer and style
    lexer = PygmentsLexer()
    try:
        formatter = get_formatter_by_name(format)
    except ClassNotFound:
        logger.error(f'No Pygment formmatter found for \'{format}\'.')
    pygment_style = PygmentsStyle(grammar)
    return pygments.highlight(code, lexer, formatter(style=pygment_style))

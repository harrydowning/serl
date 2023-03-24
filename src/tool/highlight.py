import re
import tool.logger as logger
import pygments
from pygments.style import Style
from pygments.util import ClassNotFound
from pygments.lexer import RegexLexer
from pygments.token import string_to_tokentype, Generic, Comment, Whitespace
from pygments.formatters import get_formatter_by_name
from pygments.styles import get_style_by_name

class PygmentsLexer(RegexLexer):
    flags = [re.VERBOSE]
    def __init__(self, tokens: dict, ignore: str, tokentypes: dict, **options):
        super().__init__(**options)
        self.tokens = {
            'root': [
                (pattern, string_to_tokentype(tokentypes.get(name.title(), Generic))) 
                for name, pattern in tokens.items()
            ] + [
                (r'\s', Whitespace)
                (ignore, Comment)
            ]
        }

def get_pygment_output(src: str, tokens: dict[str, str], ignore: str, 
                       tokentypes: dict[str, str], user_styles: dict[str, str],
                       style_name: str, format: str, 
                       format_options: dict) -> str:
    lexer = PygmentsLexer(tokens, ignore, tokentypes)
    try:
        style = get_style_by_name(style_name)
        for tokentype, user_style in user_styles:
            style.styles[tokentype] = user_style
    except ClassNotFound:
        logger.error(f'No Pygment style found for \'{style_name}\'.')
    
    try:
        formatter = get_formatter_by_name(format, style=style, 
                                          **format_options)
    except ClassNotFound:
        logger.error(f'No Pygment formmatter found for \'{format}\'.')

    return pygments.highlight(src, lexer, formatter)

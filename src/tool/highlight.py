import re
import tool.logger as logger
import pygments
from pygments.style import Style
from pygments.util import ClassNotFound
from pygments.lexer import RegexLexer
from pygments.token import string_to_tokentype, Generic, Comment, Whitespace
from pygments.formatters import get_formatter_by_name
from pygments.styles import get_style_by_name

def get_pygments_lexer(_tokens: dict, ignore: str, tokentypes: dict):
    class PygmentsLexer(RegexLexer):
        flags = re.VERBOSE

        tokens = {
            'root': [
                (pattern, string_to_tokentype(tokentypes.get(name.title(), Generic))) 
                for name, pattern in _tokens.items()
            ] + [
                (r'\s', Whitespace),
                (ignore, Comment)
            ]
        }
    return PygmentsLexer()

def get_pygments_output(src: str, tokens: dict[str, str], ignore: str, 
                       tokentypes: dict[str, str], user_styles: dict[str, str],
                       style_name: str, format: str, 
                       format_options: dict) -> str:
    lexer = get_pygments_lexer(tokens, ignore, tokentypes)
    try:
        style = get_style_by_name(style_name)
        for tokentype, user_style in user_styles:
            style.styles[tokentype] = user_style
    except ClassNotFound:
        logger.error(f'No Pygment style found for \'{style_name}\'.')
    
    try:
        formatter = get_formatter_by_name(format, style=style, full=True, # TODO temp
                                          **format_options)
    except ClassNotFound:
        logger.error(f'No Pygment formmatter found for \'{format}\'.')

    return pygments.highlight(src, lexer, formatter)

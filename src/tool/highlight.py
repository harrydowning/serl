import re
import tool.logger as logger
import pygments
from pygments.style import Style, StyleMeta
from pygments.util import ClassNotFound
from pygments.lexer import RegexLexer
from pygments.token import string_to_tokentype, Text, Comment, Whitespace
from pygments.formatters import get_formatter_by_name
from pygments.styles import get_style_by_name

def get_pygments_lexer(_tokens: dict, ignore: str, tokentypes: dict):
    tokentypes = {t: ttype.title() for t, ttype in tokentypes.items()}
    class PygmentsLexer(RegexLexer):
        flags = re.VERBOSE

        tokens = {
            'root': [
                (_tokens.get(name_or_pattern, name_or_pattern), 
                 string_to_tokentype(ttype)) 
                for name_or_pattern, ttype in tokentypes.items()
            ] + [
                (pattern, Text) for name, pattern in _tokens.items()
            ] + [
                (r'\s', Whitespace), # TODO may not need
                (ignore, Comment)
            ]
        }
    return PygmentsLexer()

def get_pygments_style(style: StyleMeta, user_styles: dict[str, str]):
    attrs = {
        attr: getattr(style, attr) 
        for attr in dir(style) 
        if not attr.startswith('_')
    }

    attrs['styles'] = attrs.get('styles', {}) | {
        string_to_tokentype(tokentype.title()): user_style
        for tokentype, user_style in user_styles.items()
    }
    # Create class with type(...) to allow dynamic creation of attrs
    PygmentsStyle = type('PygmentsStyle', (Style,), attrs)
    return PygmentsStyle

def parse_key_value(input: str) -> dict:
    result = {}
    str_re = r'(?s)([\'\"])(.*?)\1'
    delimiter_re = r',(?=[a-zA-Z_][a-zA-Z_0-9]*(?:=|,|$))'

    str_vals = {}
    def str_match(m):
        key = str(len(str_vals))
        str_vals[key] = m.group(1) + m.group(2) + m.group(1)
        return f'%({key})s'
    
    options_str = re.sub(str_re, str_match, input)
    options_str = re.sub(r'\s', '', options_str)
    for option in re.split(delimiter_re, options_str):
        try:
            name, value = option.split('=', 1)
        except ValueError:
            result[option] = True
            continue
        value %= str_vals
        try:
            result[name] = eval(value)
        except NameError:
            result[name] = value
        except Exception as e:
            logger.warning(f'Error with option \'{option}\', {e}')
            continue
    return result

def get_pygments_output(src: str, tokens: dict[str, str], ignore: str, 
                       tokentypes: dict[str, str], user_styles: dict[str, str],
                       format: str, format_options: dict) -> str:
    lexer = get_pygments_lexer(tokens, ignore, tokentypes)
    
    style_name = format_options.get('style', None)
    if style_name:
        try:
            style = get_style_by_name(style_name)
        except ClassNotFound:
            logger.warning(f'No Pygment style found for \'{style_name}\'. '
                           f'Default will be used.')
            style = get_style_by_name('default')
        
        format_options['style'] = get_pygments_style(style, user_styles)

    try:
        formatter = get_formatter_by_name(format, **format_options)
    except ClassNotFound:
        logger.error(f'No Pygment formmatter found for \'{format}\'.')

    return pygments.highlight(src, lexer, formatter),formatter.get_style_defs()

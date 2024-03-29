from types import SimpleNamespace
import pytest
import serl.lexer as lexer
import re, regex

class MockLexToken(object):
    def __init__(self, span=(0,0), string=None, lineno=None, value=None, allcaptures=None, groups=None):
        self.lexer = SimpleNamespace(
            lexmatch = SimpleNamespace(
                span= lambda: span,
                allcaptures=lambda: allcaptures,
                groups= lambda: groups
            ),
            lineno = lineno,
            lexpos = span[0],
            lexdata = string
        )
        self.value = value

    def __eq__(self, __value: object) -> bool:
        return __value.value == self.value and __value.lexer.lineno == self.lexer.lineno


@pytest.mark.parametrize('token, pattern, using_regex, using_cpython, t, expected', [
    ('TOK1', r':(\d+):', False, True, MockLexToken((3,8), 'aaa:123:a', 1, ':123:', groups=(':123:', '123')), MockLexToken(lineno=1, value=(':123:', '123'))),
    ('TOK2', r':(\d+):', True, True, MockLexToken((3,8), 'aaa:123:a', 2, ':123:', allcaptures=([':123:'], [':123:'], ['123'])), MockLexToken(lineno=2, value=([':123:'], ['123']))),
    ('TOK3', r'(\|(\d+))+\n', True, True, MockLexToken((5,20), 'start|1|22|333|4444\nend', 2, '|1|22|333|4444\n', allcaptures=(['|1|22|333|4444\n'],['|1|22|333|4444\n'], ['|1', '|22', '|333', '|4444'], ['1', '22', '333', '4444'])), MockLexToken(lineno=3, value=(['|1|22|333|4444\n'], ['|1', '|22', '|333', '|4444'], ['1', '22', '333', '4444']))),
])
def test_get_pattern_func(token, pattern, using_regex, using_cpython, t, expected):
    lexer.using_cpython = using_cpython
    lexer.lex.re = regex if using_regex and using_cpython else re
    g_span = (0, len(t.value))
    pattern_func = lexer.get_pattern_func(token, pattern, using_regex, g_span)
    assert pattern_func.__doc__ == pattern
    assert pattern_func.__name__ == token
    t = pattern_func(t)
    assert t == expected


def test_get_ignore_func():
    pattern = '.*!@#$%^&*()'
    ignore_func = lexer.get_ignore_func(pattern)
    assert ignore_func.__doc__ == pattern
    assert ignore_func.__name__ == 'ignore'


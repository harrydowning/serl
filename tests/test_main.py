import sys, os
import pytest
import tool.main as main
from test_utils import tokens, token_split, exp_tokens

def test_token_expansion():
    actual = main.token_expansion(tokens, token_split)
    expected = exp_tokens
    assert actual == expected
    # ensure order is also preserved
    assert list(actual.keys()) == list(expected.keys())

base_args = {
    '--debug': False,
    '--help': False,
    '--requirements': None,
    '--strict': False,
    '--version': False,
    '<dir>': None,
    '<input>': [],
    '<language>': '',
    'link': False
}

link_args = {
    '--': True,
    '--debug': False,
    '--help': False,
    '--requirements': None,
    '--strict': False,
    '--version': False,
    '<input>': [],
    '<language>': ''
}

args_data = [
    (['path/to/link1', '-o', 'example.txt'], True, 
     link_args | {'<language>': 'link1', '<input>': ['-o', 'example.txt']}),
    (['path/to/link2', '--debug', '--', 'example.txt'], True, 
     link_args | {'<language>': 'link2', '--debug': True, 
                  '<input>': ['example.txt']}),
    (['path/to/tool', '--strict', 'lang1', '--debug', 'example.txt'], False,
     base_args | {'<language>': 'lang1', '--strict': True,
                  '<input>': ['--debug', 'example.txt']}),
    (['path/to/tool', 'link', 'lang1', 'path/to/dir'], False,
     base_args | {'<language>': 'lang1', '<dir>': 'path/to/dir', 
                  'link': True}),
]

@pytest.mark.parametrize("args, is_link, expected", args_data)
def test_get_args(args, is_link, expected):
    os.path.islink = lambda x: is_link
    sys.argv = args
    actual = main.get_args()
    assert actual == expected

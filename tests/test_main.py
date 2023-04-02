import sys, os, copy
import pytest
import serl.main as main
from test_utils import tokens, token_split, exp_tokens

grammar_map = {
    'S': '',
    'N1': ['', ''],
    'N2': [''],
}

code = {
    'main': ['cd1', 'cd2'],
    'S': 'cd3',
    'N1': ['cd4', 'cd5'],
}

code_without_main = {
    'S': 'cd3',
    'N1': ['cd4', 'cd5'],
}

commands = {
    'N1': ['cm1'],
    'N2': 'cm2'
}

@pytest.mark.parametrize('name, pos, expected_code, expected_command', [
    ('N1', 1, 'cd5', None), ('S', 0, 'cd3', None), ('N2', 0, None, 'cm2'),
    ('N1', 0, 'cd4', 'cm1')
])
def test_Functionality_get(name, pos, expected_code, expected_command):
    functionality = main.Functionality(code, commands, grammar_map)
    actual_code = functionality.get_code(name, pos)
    actual_command = functionality.get_command(name, pos)
    assert actual_code == expected_code
    assert actual_command == expected_command

@pytest.mark.parametrize('code, commands, expected', [
    (code, commands, code['main']), (code_without_main, commands, None)
])
def test_Functionality_main(code, commands, expected):
    actual = main.Functionality(code, commands, grammar_map).main
    assert actual == expected

def test_token_expansion():
    actual = main.token_expansion(tokens, token_split)
    expected = exp_tokens
    assert actual == expected
    # ensure order is also preserved
    assert list(actual.keys()) == list(expected.keys())

file = 'path/to/file'
@pytest.mark.parametrize('file, platform, expected', [
    (file, 'posix', file), (file, 'nt', file + '.exe')
])
def test_extension(file, platform, expected):
    tmp = os.name
    os.name = platform
    actual = main.extension(file)
    assert actual == expected
    os.name = tmp

@pytest.mark.parametrize('argv,  base_args_expected, args_expected', [
    (['link/for/lang1'], {'<command>': 'run'}, {'<language>': 'lang1'}),
    (['link/for/lang1', '--verbose', '--'], {}, {'--verbose': True, '<args>': []}),
    (['link/for/lang1', '--verbose'],  {}, {'--verbose': False, '<args>': ['--verbose']})
])
def test_get_symlink_args(argv, base_args_expected, args_expected):
    sys.argv = argv
    filename = main.extension(argv[0])
    version = '0.0.1'
    base_args_actual, args_actual = main.get_symlink_args(filename, version)

    for k, v in base_args_expected.items():
        assert base_args_actual[k] == v
    
    for k, v in args_expected.items():
        assert args_actual[k] == v

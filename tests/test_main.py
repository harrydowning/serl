import sys, os, subprocess
from types import SimpleNamespace
import pytest
import serl.main as main
from test_utils import tokens, token_split, exp_tokens

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

def test_exec_and_eval():
    pass

env = {
    'dict': {
        'key': 'v1'
    },
    'list': ['v2', 'v3', 'v4'],
    'var': 'v5',
    'f': lambda *args, **kwargs: 'v6',
    'tf': main.Traversable(lambda *args, **kwargs: 'v7')
}

@pytest.mark.parametrize('command, expected', [
    ('cmd ${{HOME}}', 'cmd ${HOME}'),
    ('cmd {dict[key]}', 'cmd v1'),
    ('cmd {list[1]}', 'cmd v3'),
    ('cmd {var}', 'cmd v5'),
    ('cmd {f}', f'cmd {env["f"]}'),
    ('cmd {tf}', f'cmd v7'),
])
def test_run_command(command, expected):
    tmp_run = subprocess.run
    
    def correct_call(command, *args, **kwargs):
        assert command == expected
        return SimpleNamespace(stdout=None)
    subprocess.run = correct_call
    main.run_command(command, env)
    subprocess.run = tmp_run

def test_get_execute_func():
    pass

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

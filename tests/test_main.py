import sys, os, subprocess
from types import SimpleNamespace
import pytest
import serl.main as main
from serl.parser import SerlAST
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

@pytest.mark.parametrize(
        'code, global_env, local_env, expected,'
        'expected_global_env, expected_local_env', 
        [
            ('', {}, None, None, {}, None),
            ('var = "v2"; pass', {}, None, None, {'var': 'v2'}, None),
            ('var', {'var': 'v1'}, None, 'v1', {'var': 'v1'}, None),
            ('var = "v3"; new = var + " v2"', {'var': 'v1'}, None, 'v3 v2', {'var': 'v3'}, None),
            ('global var; var = "v3"; var', {'var': 'v1'}, {}, 'v3', {'var': 'v3'}, {}),
            ('var = "v3"; 3 + 2', {'var': 'v1'}, {}, 5, {'var': 'v1'}, {'var': 'v3'}),
            ('a = 5\nreturn a', {}, {}, 5, {}, {'a': 5}),
        ]
)
def test_exec_and_eval(
    code, global_env, local_env, expected, 
    expected_global_env, expected_local_env
):
    actual = main.exec_and_eval(code, global_env, local_env)
    assert actual == expected
    global_env.pop('__builtins__', None)
    assert global_env == expected_global_env
    assert local_env == expected_local_env

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
    def mock_run(command, *args, **kwargs):
        assert command == expected
        return SimpleNamespace(stdout=None)
    subprocess.run = mock_run
    main.run_command(command, env)
    subprocess.run = tmp_run

code = {
    'NT0': [
        'f"{var} {T0}"',
        '''
first_NT1 = NT1[0]()
second_NT1 = NT1[1](pass_down = "pdv1")
NT2 = NT2(local_var = "lv1").strip()
first_NT1 + " " + second_NT1 + " " + NT2
        '''
    ],
    'NT1': [
        'return "(" + pass_down + ")"',
        'return T1.upper()'
    ],
    'NT2': [
        '$ echo {local_var} {var}'
    ]
}

global_env = {
    'var': 'gv1',
}

@pytest.mark.parametrize('serl_ast, local_env, expected', [
    (SerlAST('NT0', 0, {'T0': ['v1']}), {}, 'gv1 v1'),
    (SerlAST('NT0', 1, {
                'NT1': [
                    SerlAST('NT1', 1, {'T1': ['v2']}),
                    SerlAST('NT1', 0, {})
                ],
                'NT2': [SerlAST('NT2', 0, {'var': ['v3']})]
             }), 
    {}, 'V2 (pdv1) lv1 v3'),
    (SerlAST('NT0', 2, {'var': ['v1']}), {'local_var': 'v2'}, {'var': 'v1'}),
    (SerlAST('NT2', 0, {'var': ['v1']}), {'local_var': 'v2'}, 'v2 v1\n'),
])
def test_get_execute_func(serl_ast, local_env, expected):
    actual_execute = main.get_execute_func(serl_ast, code, global_env)
    actual = actual_execute(**local_env)
    assert actual == expected


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

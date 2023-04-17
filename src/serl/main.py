import sys
init_modules = sys.modules.copy().keys()

import os
import fileinput
import subprocess
import pathlib
import re
import venv
import site
import shutil
import ast
import glob
import traceback

from serl.lexer import build_lexer
from serl.parser import build_parser, SerlAST
import serl.utils as utils
import serl.logger as logger
from serl.highlight import get_pygments_output, parse_key_value
from serl.config import get_config, get_config_dir, get_config_env_dir, \
    get_config_text, system_config_exists, system_config_languages
from serl.constants import CLI, SYMLINK_CLI, CLI_COMMANDS, NAME, VERSION, \
    DEFAULT_REF, SHELL_CHAR, VENV_CONFIG, EXCEPTION_ATTR 

from docopt import docopt
import networkx as nx

class Traversable():
    def __init__(self, f):
        self.f = f
    
    def __call__(self, *args, **kwargs):
        return self.f(*args, **kwargs)

class TraversableFormat(dict):
    def __getitem__(self, __key):
        __val = super().__getitem__(__key)
        if isinstance(__val, Traversable):
            return __val()
        return __val

    def __missing__(self, key):
        return key

def token_expansion(tokens: dict[str, str], split: list[str]) -> dict[str, str]:
    repl_tokens = utils.get_repl_tokens(tokens, split)
    token_graph = nx.DiGraph(utils.get_token_graph(repl_tokens))
    cycles = list(nx.simple_cycles(token_graph))

    if cycles:
        cycle_nodes = {node for cycle in cycles for node in cycle}
        token_graph.remove_nodes_from(cycle_nodes)
        token_map = dict(zip(repl_tokens.keys(), tokens.keys()))
        
        for i, cycle in enumerate(cycles):
            cycle = map(lambda tok: f'\'{token_map[tok]}\'', cycle)
            msg = (f'Cyclic reference involving {", ".join(cycle)}.'
                    ' Preceding token(s) will not be expanded.')
            logger.warning(msg)
            
            shown = i + 1 
            remaining = len(cycles) - shown
            if shown >= len(tokens) and remaining > 1:
                logger.warning(f'[{remaining} more cycles...]')
                break

    exp_order = list(nx.topological_sort(token_graph))
    exp_tokens = utils.expand_tokens(exp_order, repl_tokens)
    return dict(zip(tokens.keys(), exp_tokens.values()))

def extension(file: str) -> str:
    if os.name == 'nt':
        file += '.exe'
    return file

def requirements(req: str | None):
    if req == None:
        logger.warning('No requirements specified.')
        return
    reqs = re.split(r'\n', req.strip())
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', '--no-color',
                               'install', '-qqq', *reqs])
    except subprocess.CalledProcessError as e:
        exit(e.returncode)

def highlight(args: dict, src: str, tokens: dict, ignore: str, 
              tokentypes: dict, user_styles: dict):
    filename = args['--highlight']
    format = args['--format'] or os.path.splitext(filename)[1][1:]
    format_options = parse_key_value(args['--format-options'] or '')
    style_defs_arg = args['--style-defs-arg']
        
    output = get_pygments_output(src, tokens, ignore, tokentypes, user_styles, 
                                 format, format_options, style_defs_arg)
    highlighted_src, style_defs = output
    if type(highlighted_src) == bytes:
        mode = 'wb'
    else:
        mode = 'w'

    with open(filename, mode) as file:
        file.write(highlighted_src)
    
    if args['--style-defs'] and style_defs:
        with open(args['--style-defs'], 'w') as file:
            file.write(style_defs)
    exit(0)

def command_line_link(args):
    language = args['<language>']
    dir = args['<dir>'] or ''
    
    src = extension(sys.argv[0])
    dst = extension(os.path.join(dir, language))

    if not system_config_exists(language):
        logger.warning(f'No system config for language \'{language}\'')

    try:
        os.symlink(src, dst)
        print(f'Successfully linked \'{language}\'.')
    except Exception as e:
        logger.error(f'Symbolic link error: {e}', code=1)

def command_line_run(args):
    language = args['<language>']
    lang_name = utils.get_language_name(language)
    config = get_config(language)

    venv_name = config.get('environment', None)
    venv_created = False
    if venv_name:
        for sitepackage in site.getsitepackages():
            sys.path.remove(sitepackage)
        
        venv_path = os.path.join(get_config_env_dir(), venv_name)
        if not glob.glob(os.path.join(venv_path, VENV_CONFIG)):
            logger.info(f'Creating virtual environment \'{venv_name}\'.', 
                        important=True)
            venv.create(venv_path, with_pip=True)
            venv_created = True
        
        for sitepackage in site.getsitepackages([venv_path]):
            sys.path.append(sitepackage)
        
        context = venv.EnvBuilder().ensure_directories(venv_path)
        sys.executable = context.env_exe

    if args['--requirements'] or venv_created:
        logger.info(f'Installing requirements.', important=True)
        requirements(config.get('requirements', None))

    version = config.get('version', None)
    usage = config.get('usage', None)
    
    inputs = args['<args>']
    debug_parser_file = args['--debug-parser']
    debug_lexer = args['--debug-lexer']

    # User language docopt
    if usage != None:
        language_args = docopt(usage, argv=inputs, version=version)
        src_input = language_args.get('<src>', None)
        if not(isinstance(src_input, str) or src_input == None):
            logger.error('File to be parsed must be specified in usage pattern' 
                         ' as \'<src>\' (filepath), \'[<src>]\' '
                         '(filepath or stdin) or nothing (stdin).', code=1)
    else:
        language_args = {}
        src_input = next(iter(inputs), None) # First element if it exists
    
    # Read input file if prsent else read from stdin
    with fileinput.input(files=src_input or ()) as file:
        src = ''.join(file)
    
    meta = config.get('meta', {})
    meta_tokens = meta.get('tokens', {})

    tokens = config.get('tokens', {})
    ref = meta_tokens.get('ref', DEFAULT_REF)
    using_regex = meta_tokens.get('regex', False)
    ignore = meta_tokens.get('ignore', '.')
    flags = meta_tokens.get('flags', 'VERBOSE')
    
    tokens_copy = tokens.copy()
    if ref != None:
        # if 'token' not used assume given string is prefix of token repl.
        ref += '' if 'token' in ref else 'token'
        logger.info(f'Performing token expansion with \'ref\' pattern '
                    f'\'{ref}\' (default: \'{DEFAULT_REF}\')')
        tokens = token_expansion(tokens, ref.split('token'))
    
    for token in tokens_copy:
        tb, ta = tokens_copy[token].strip(), tokens[token].strip()
        if tb != ta: # TODO case where expansion is actually equal?
            logger.info(f'Token \'{token}\' expanded: \'{tb}\' -> \'{ta}\'')

    precedence = config.get('precedence', [])
    grammar = config['grammar']
    error_sym = config.get('error', None)
    meta_grammar = meta.get('grammar', {})
    permissive = meta_grammar.get('permissive', True)

    token_map = {k: f'TERMINAL{i}' for i, k, in enumerate(tokens.keys())}
    grammar_map = {k: f'NONTERMINAL{i}' for i, k in enumerate(grammar.keys())}
    common_keys = set(token_map.keys()).intersection(grammar_map.keys())
    s = '\', \''
    if common_keys:
        logger.error(f'Grammar identifiers \'{s.join(common_keys)}\' already '
                     f'used in tokens', code=1)
    
    symbol_map = token_map | grammar_map
    grammar = utils.normalise_grammar(symbol_map, grammar)

    tokens_used, implicit_map = utils.get_tokens_in_grammar(token_map, 
                                                            error_sym, grammar)
    tokens = utils.keep_keys_in_list(tokens, tokens_used)
    token_map = utils.keep_keys_in_list(token_map, tokens_used) | implicit_map
    tokens |= {k: re.escape(k) for k, v in implicit_map.items()}
    symbol_map = token_map | grammar_map
    
    if error_sym in symbol_map:
        logger.error(f'Multiple definitions for \'{error_sym}\'.', code=1)
    elif error_sym:
        symbol_map[error_sym] = 'error'

    if len(implicit_map):
        logger.info(f'Implicit tokens: \'{s.join(implicit_map.keys())}\'')

    if args['--highlight']:
        tokentypes = config.get('tokentypes', {})
        user_styles = config.get('styles', {})
        highlight(args, src, tokens, ignore, tokentypes, user_styles)

    lexer = build_lexer(tokens, token_map, ignore, using_regex, flags)
    parser = build_parser(
        lang_name, list(token_map.values()), symbol_map, grammar, precedence,
        debug_parser_file
    )

    # Debug lexer
    lexer_clone = lexer.clone()
    flipped_token_map = utils.flip_dict(token_map)
    lexer_clone.input(src)
    lines = src.count('\n') + 1
    tokens_by_line = [[] for _ in range(lines)]
    
    while True:
        tok = lexer_clone.token()
        if not tok: 
            break
        tokens_by_line[tok.lineno - 1].append(flipped_token_map[tok.type])
    
    logger.info(f'Tokens Found:', important=debug_lexer)
    for i, line in enumerate(tokens_by_line):
        lineno = str(i + 1).rjust(len(str(lines)), ' ')
        logger.info(f'  {lineno}: {" ".join(line)}', important=debug_lexer)
    # Debug lexer

    serl_ast = parser.parse(src, lexer=lexer, tracking=True)
    if (not permissive and logger.error_seen) or not serl_ast:
        logger.error('Parse Failed', code=1)
    
    code = utils.normalise_dict(config['code'])
    main_code = utils.get_main_code(code, grammar_map)
    
    for code_name, code_list in code.items():
        internal_name = grammar_map.get(code_name, None)
        if not internal_name: continue
        for i in range(len(grammar[internal_name])):
            value = code_list[i] if len(code_list) > i else None
            if value == None:
                logger.warning(f'Code missing for $.code.{code_name}[{i}]')
    
    # Remove module cache to allow for correct user import
    for module in sys.modules.copy().keys():
        if not module in init_modules:
            del sys.modules[module]

    global_env = {
        '__name__': lang_name,
        'args': language_args,
    }
    execute_func = get_execute_func(serl_ast, code, global_env)

    try:
        if main_code:
            global_env[serl_ast[0]] = execute_func
            result = exec_or_error(main_code[0], 0, main_code[1], global_env)
        else:
            result = execute_func()
    except SyntaxError as err:
        err.__traceback__ = None
        err.__context__ = None
        err.__notes__ = None
        logger.error(f'In {err.filename}:\n\n', exc_info=True, code=1)
    except subprocess.CalledProcessError as err:
        err.__notes__ = None
        logger.error(f'In {err.filename}:\n\n{err.stderr}',code=err.returncode)
    except Exception as err:
        frames = traceback.extract_tb(err.__traceback__)
        frame = next((frame for frame in frames[::-1] 
                      if frame.filename == '<string>'), frames[-1])
        lineno = frame.lineno
        err.__traceback__ = None
        err.__context__ = None
        code_name, i = getattr(err, EXCEPTION_ATTR, ('', -1))
        filename = f'$.code.{code_name}[{i}]'
        code_lines = code[code_name][i].split('\n')
        code_line = ':'
        if frame.filename == '<string>' and lineno - 1 < len(code_lines):
            code_line = f', line {lineno}:\n\n  {code_lines[lineno - 1]}'
        err.__notes__ = None
        logger.error(f'In {filename}{code_line}\n\n', exc_info=True,code=1)

    if result:
        print(result, end='')
    
def exec_and_eval(code, global_env, local_env=None):
    code_ast = ast.parse(code)

    try:
        last_stmt = code_ast.body.pop()
        expr = ast.Expression(last_stmt.value)
    except AttributeError:
        return exec(code, global_env, local_env)
    except IndexError:
        return None

    exec(compile(code_ast, '<string>', mode='exec'), global_env, local_env)
    return eval(compile(expr, '<string>', mode='eval'), global_env, local_env)

def run_command(command: str, env: dict):
    command = command.format_map(TraversableFormat(**env))
    return subprocess.run(command, capture_output=True, text=True, shell=True, 
                          check=True).stdout

def exec_or_error(name, i, code_str, global_env, local_env=None):
    try:
        if code_str.startswith(SHELL_CHAR):
            local_env = local_env or {}
            local_env = {'locals()': local_env} | local_env
            return run_command(code_str[1:], global_env | local_env)
        else:
            return exec_and_eval(code_str, global_env, local_env)
    except Exception as err:
        if not getattr(err, EXCEPTION_ATTR, None):
            setattr(err, EXCEPTION_ATTR, (name, i))
        raise

def get_execute_func(serl_ast: SerlAST, code: dict, global_env: dict):
    name, i, value = serl_ast
    env = {}
    for k, v in value.items():
        env[k] = [get_execute_func(e, code, global_env) 
                  if isinstance(e, SerlAST) else e for e in v]
        env[k] = env[k][0] if len(env[k]) == 1 else env[k]
    
    active = True
    def execute(**local_env):
        # Make sure the function can only be called once
        nonlocal active
        if not active:
            return None
        active = False

        code_list = code.get(name, None)
        code_str = code_list[i] if code_list and len(code_list) > i else None
        
        if not code_str:
            return env # TODO should 'None' be returned?

        return exec_or_error(name, i, code_str, global_env, local_env | env)
    
    return Traversable(execute)

def command_line_install(args):
    language = args['<language>']
    alias = args['<alias>'] or utils.get_language_name(language)
    upgrade = args['--upgrade']
    
    config_text = get_config_text(language)
    config_dir = get_config_dir()
    filename = os.path.join(config_dir, alias)
    
    if os.path.isfile(filename) and not upgrade:
        logger.error(f'Language \'{alias}\' already exists. '
                     f'Use -U or --upgrade to override.', code=1)
    
    with open(filename, 'w') as file:
        file.write(config_text)
    print(f'Successfully installed \'{alias}\'.')

def command_line_uninstall(args: dict):
    languages = args['<language>']
    envs = args['<env>']
    remove_venv = args['--venv']
    remove, files, prefix = os.remove, languages, get_config_dir()
    if remove_venv:
        remove, files, prefix = shutil.rmtree, envs, get_config_env_dir()
    
    for file in files:
        path = os.path.join(prefix, file)
        try:
            remove(path)
            print(f'Successfully uninstalled \'{file}\'.')
        except FileNotFoundError:
            logger.warning(f'Skipping \'{file}\' as it is not already '
                           f'installed.')  

def command_line_list(args):
    languages = system_config_languages()
    config_env_dir = get_config_env_dir() + os.sep
    glob_path = os.path.join(config_env_dir, '**', VENV_CONFIG)
    envs = glob.glob(glob_path, recursive=True)
    envs = [
        str(pathlib.Path(path).parent.resolve()).removeprefix(config_env_dir) 
        for path in envs
    ]
    
    files, name = languages, 'languages'
    if args['--venv']:
        files, name = envs, 'environments'
    
    if files == []:
        print(f'No {name} installed.')
    else:
        print(*files, sep='\n')

def get_symlink_args(filename, version) -> dict:
    # Stop initial args acting on the tool and not the language
    if not '--' in sys.argv:
        sys.argv.insert(1, '--')
    
    args = docopt(SYMLINK_CLI, version=version, options_first=True)

    if args['--where']:
        print(pathlib.Path(filename).resolve())
        exit(0)

    args['<language>'] = utils.get_language_name(filename)
    base_args = {'<command>': 'run'}
    return base_args, args

def get_args(version):
    base_args = docopt(CLI, version=version, options_first=True)
    command = base_args['<command>']
    argv = base_args['<args>']
    cli_command = CLI_COMMANDS.get(command, None)
    
    if cli_command == None:
        print(CLI)
        exit(0)

    args =  docopt(cli_command, argv=argv, version=version, options_first=True)
    
    if command == 'help':
        print(CLI_COMMANDS.get(args['<command>'], CLI))
        exit(0)
    
    return base_args, args

def main():
    version = f'{NAME} {VERSION}'
    filename = extension(sys.argv[0])

    if os.path.islink(filename):
        base_args, args = get_symlink_args(filename, version)
    else:
        base_args, args = get_args(version)

    logger.verbose = base_args.get('--verbose', False) or \
        args.get('--verbose', False)
    # TODO sys.setrecursionlimit(20000)
    try:
        globals()[f'command_line_{base_args["<command>"]}'](args)
    except Exception:
        if not logger.error_seen:
            raise
        raise # TODO exit(1)

import sys
init_modules = sys.modules.copy().keys()

import os, fileinput, subprocess, pathlib, re, venv, site, shutil, ast
from docopt import docopt
import networkx as nx
from serl.lexer import build_lexer
from serl.parser import build_parser, SerlAST
import serl.utils as utils
import serl.logger as logger
from serl.highlight import get_pygments_output, parse_key_value
from serl.config import get_config, get_config_dir, get_config_env_dir, \
    get_config_text, system_config_exists, system_config_languages
from serl.constants import CLI, SYMLINK_CLI, CLI_COMMANDS, NAME, VERSION, \
    DEFAULT_REF, RETURN_VAR

class Functionality():
    def __init__(self, code: dict, commands: dict, grammar_map: dict):
        self.code = utils.normalise_dict(code)
        self.commands = utils.normalise_dict(commands)

        items = self.code.items()
        name, cd = next(iter(items), None)
        self.main = cd if not name in grammar_map else None

        dups = utils.get_dups(self.code, self.commands)
        if len(dups) > 0:
            msg = (f'Functionality defined in both \'code\' and \'command\' '
                   f'for {", ".join(map(str, dups))}, \'code\' will take '
                   f'precedence.')
            logger.warning(msg)

    def _get(self, d: dict, name: str, pos: int) -> str | None:
        v = d.get(name, None)
        if v and len(v) > pos:
            return v[pos]
        return None

    def get_code(self, name: str, pos: int) -> str | None:
        return self._get(self.code, name, pos)

    def get_command(self, name: str, pos: int) -> str | None:
        return self._get(self.commands, name, pos)

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
        
    output = get_pygments_output(src, tokens, ignore, tokentypes, user_styles, 
                                 format, format_options)
    highlighted_src, style_defs = output
    if type(highlighted_src) == bytes:
        mode = 'wb'
    else:
        mode = 'w'

    with open(filename, mode) as file:
        file.write(highlighted_src)
    
    if args['--style-defs']:
        with open(args['--style-defs'], 'w') as file:
            file.write(style_defs)
    exit(0)

def link_command(args):
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
        logger.error(f'Symbolic link error: {e}')

def run_command(args):
    language = args['<language>']
    lang_name = utils.get_language_name(language)
    config = get_config(language)

    env = config.get('environment', None)
    env_created = False
    if env:
        for sitepackage in site.getsitepackages():
            sys.path.remove(sitepackage)
        
        env_name = os.path.join(get_config_env_dir(), env)
        if not os.path.exists(env_name):
            logger.info(f'Creating virtual environment \'{env}\'.', 
                        important=True)
            venv.create(env_name, with_pip=True)
            env_created = True
        
        for sitepackage in site.getsitepackages([env_name]):
            sys.path.append(sitepackage)
        
        context = venv.EnvBuilder().ensure_directories(env_name)
        sys.executable = context.env_exe

    if args['--requirements'] or env_created:
        logger.info(f'Installing requirements.', important=True)
        requirements(config.get('requirements', None))

    version = config.get('version', None)
    usage = config.get('usage', None)
    
    inputs = args['<args>']
    debug_file = args['--debug']

    # User language docopt
    if usage != None:
        language_args = docopt(usage, argv=inputs, version=version)
        src_input = language_args.get('<src>', None)
        if not(isinstance(src_input, str) or src_input == None):
            logger.error('File to be parsed must be specified in usage pattern' 
                         ' as \'<src>\' (filepath), \'[<src>]\' '
                         '(filepath or stdin) or nothing (stdin).')
    else:
        src_input = next(iter(inputs), None) # First element if it exists
    
    # Read input file if prsent else read from stdin
    with fileinput.input(files=src_input or ()) as file:
        src = ''.join(file)
    
    meta = config.get('meta', {})
    meta_tokens = meta.get('tokens', {})

    tokens = config['tokens']
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
        if tb != ta:
            logger.info(f'Token \'{token}\' expanded: \'{tb}\' -> \'{ta}\'')

    precedence = config.get('precedence', [])
    sync = config.get('sync', [])
    grammar = config['grammar']
    permissive = meta.get('permissive', True)

    token_map = {k: f'TERMINAL{i}' for i, k, in enumerate(tokens.keys())}
    grammar_map = {k: f'NONTERMINAL{i}' for i, k in enumerate(grammar.keys())}
    common_keys = set(token_map.keys()).intersection(grammar_map.keys())
    if common_keys:
        s = '\', \''
        logger.error(f'Grammar identifiers \'{s.join(common_keys)}\' already '
                     f'used in tokens')
    
    symbol_map = token_map | grammar_map
    grammar = utils.normalise_grammar(symbol_map, grammar)

    tokens_in_grammar = utils.get_tokens_in_grammar(token_map, grammar)
    tokens = utils.filter_dict_keys(tokens, tokens_in_grammar)
    token_map = utils.filter_dict_keys(token_map, tokens_in_grammar)
    symbol_map = token_map | grammar_map

    if args['--highlight']:
        tokentypes = config.get('tokentypes', {})
        user_styles = config.get('styles', {})
        highlight(args, src, tokens, ignore, tokentypes, user_styles)

    lexer = build_lexer(tokens, token_map, ignore, using_regex, flags)
    parser = build_parser(lang_name, list(token_map.values()), symbol_map, 
                          grammar, precedence, debug_file, sync, permissive)
    # lexer.input(src)
    # while True:
    #     tok = lexer.token()
    #     if not tok: 
    #         break      # No more input
    #     print(tok)

    # serl_ast = parser.parse(src, lexer=lexer)
    code = config.get('code', {})
    commands = config.get('commands', {})
    functionality = Functionality(code, commands, grammar_map)
    
    # Remove module cache to allow for correct user import
    for module in sys.modules.copy().keys():
        if not module in init_modules:
            del sys.modules[module]

    # root_execute = get_execute_func(ast, functionality, global_env)
    # global_env = {
    #     '__name__': lang_name,
    #     'args': language_args,
    #     #serl_ast[0]: root_execute
    # }

    # if functionality.main:
    #     main = functionality.main[0]
    #     result = exec_and_eval(main, global_env)
    #     print(result)
    #     print(global_env.keys())
    # else:
    #     result = root_execute()
    
    # if result:
    #     print(result, end='')

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

def get_execute_func(ast: SerlAST, functionality: Functionality, global_env: dict):
    name, i, value = ast
    env = {}
    for k, v in value.items():
        if isinstance(v, list):
            env[k] = [get_execute_func(e, functionality, global_env) 
                      if isinstance(e, SerlAST) else e for e in v]
        else:
            exec_func = get_execute_func(v, functionality, global_env)
            env[k] = exec_func if isinstance(v, SerlAST) else v
    
    active = True
    def execute(**local_env):
        # Make sure the function can only be called once
        nonlocal active
        if not active:
            return None
        active = False

        code = functionality.get_code(name, i)
        command = functionality.get_command(name, i)
        if code:
            local_env |= env
            return exec_and_eval(code, global_env, local_env)
        elif command:
            # TODO add global and local vars to env TODO how to invoke code/command of child nonterminals
            env = os.environ.copy() | {}
            return subprocess.run(command, capture_output=True, text=True, 
                                  shell=True, env=env, check=True).stdout
        else:
            return env
    return execute

def install_command(args):
    language = args['<language>']
    alias = args['<alias>'] or utils.get_language_name(language)
    upgrade = args['--upgrade']
    
    config_text = get_config_text(language)
    config_dir = get_config_dir()
    filename = os.path.join(config_dir, alias)
    
    if os.path.isfile(filename) and not upgrade:
        logger.error(f'Language \'{alias}\' already exists. '
                     f'Use -U or --upgrade to override.')
    
    with open(filename, 'w') as file:
        file.write(config_text)
    print(f'Successfully installed \'{alias}\'.')

def uninstall_command(args: dict):
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

def list_command(args):
    languages = system_config_languages()
    envs = os.listdir(get_config_env_dir())
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
    logger.strict = base_args.get('--strict', False) or \
        args.get('--strict', False)

    globals()[f"{base_args['<command>']}_command"](args)

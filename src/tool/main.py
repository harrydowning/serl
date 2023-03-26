import sys, os, fileinput, subprocess, pathlib, re, venv
from docopt import docopt
import networkx as nx
from tool.lexer import build_lexer
from tool.parser import build_parser, AST
import tool.utils as utils
import tool.logger as logger
from tool.highlight import get_pygments_output
from tool.config import get_config, get_config_dir, get_config_env_dir, \
    get_config_text, system_config_exists, system_config_languages
from tool.constants import CLI, SYMLINK_CLI, CLI_COMMANDS, NAME, VERSION, \
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
    style_name = args['--style'] or 'default'
    format = args['--format'] or filename.split('.')[-1]
    format_options_str = re.sub(r'\s', '', args['--format-options'] or '') 
    format_options = {
        name: eval(value)
        for option in args['--format-options'].split(',')
        for name, value in option.split('=')
    }

    highlighted_src = get_pygments_output(src, tokens, ignore, tokentypes, 
                                         user_styles, style_name, format, 
                                         format_options)
    
    if type(highlighted_src) == bytes:
        mode = 'wb'
    else:
        mode = 'w'

    with open(filename, mode) as file:
        file.write(highlighted_src)
    exit(0)

def link(args):
    lang_name = utils.lang_name(args['<language>'])
    dir = args['<dir>'] or ''
    
    src = extension(sys.argv[0])
    dst = extension(os.path.join(dir, f'{lang_name}'))

    if not system_config_exists(lang_name):
        logger.warning(f'No system config for language \'{lang_name}\'')

    try:
        os.symlink(src, dst)
    except Exception as e:
        logger.error(f'Symbolic link error: {e}')

def run(args):
    language = args['<language>']
    lang_name = utils.lang_name(language)
    config = get_config(language)

    # env = config.get('environment', None)
    # if env:
    #     config_env_dir = get_config_env_dir()
    #     env_name = os.path.join(config_env_dir, f'venv-{env}')
    #     venv.create(env_name, with_pip=True)
    #     context = venv.EnvBuilder().ensure_directories(env_name)

    if args['--requirements']:
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
                         ' as \'<src>\' (file path), \'[<src>]\' '
                         '(file path or stdin) or nothing (stdin).')
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
    
    if ref != None:
        # if 'token' not used assume given string is prefix of token repl.
        ref += '' if 'token' in ref else 'token'
        logger.info(f'Performing token expansion with \'ref\' pattern '
                    f'\'{ref}\' (default: \'{DEFAULT_REF}\')')
        tokens = token_expansion(tokens, ref.split('token'))
    
    logger.info('===== TOKENS =====')
    for token, pattern in tokens.items():
        logger.info(f'{token}: \'{pattern.strip()}\'')
    logger.info('===== TOKENS =====')

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

    lexer = build_lexer(tokens, token_map, ignore, using_regex)
    parser = build_parser(lang_name, list(token_map.values()), symbol_map, 
                          grammar, precedence, debug_file, sync, permissive)
    # lexer.input(src)
    # while True:
    #     tok = lexer.token()
    #     if not tok: 
    #         break      # No more input
    #     print(tok)

    # ast = parser.parse(src, lexer=lexer)
    code = config.get('code', {})
    commands = config.get('commands', {})
    functionality = Functionality(code, commands, grammar_map)

    # root_execute = get_execute_func(ast, functionality, global_env)
    # global_env = {
    #     '__name__': lang_name,
    #     'args': language_args,
    #     ast[0]: root_execute
    # }

    # if functionality.main:
    #     main = [cd for cd in functionality.main if cd != None]
    #     for cd in main: 
    #         exec(cd, global_env)
    # else:
    #     global_env[RETURN_VAR] = root_execute()
    
    # result = global_env.get(RETURN_VAR, None)
    # if result:
    #     print(result, end='')

def get_execute_func(ast: AST, functionality: Functionality, global_env: dict):
    name, i, value = ast
    env = {}
    for k, v in value.items():
        if isinstance(v, list):
            env[k] = [get_execute_func(e, functionality, global_env) 
                      if isinstance(e, AST) else e for e in v]
        else:
            exec_func = get_execute_func(v, functionality, global_env)
            env[k] = exec_func if isinstance(v, AST) else v
    
    active = True
    def execute(**local_env):
        # Make sure the function can only be called once
        nonlocal active
        if not active:
            return None
        active = False

        cd = functionality.get_code(name, i)
        cm = functionality.get_command(name, i)
        if cd:
            local_env |= env
            exec(cd, global_env, local_env)
            return local_env.get(RETURN_VAR, None)
        elif cm:
            # TODO add global and local vars to env TODO how to invoke code/command of child nonterminals
            env = os.environ.copy() | {}
            return subprocess.run(cm, capture_output=True, text=True, 
                                  shell=True, env=env, check=True).stdout
        else:
            return env
    return execute

def install(args):
    language = args['<language>']
    alias = args['<alias>'] or utils.lang_name(language)
    upgrade = args['--upgrade']
    
    config_text = get_config_text(language)
    config_dir = get_config_dir()
    filename = os.path.join(config_dir, f'{alias}.yaml')
    
    if os.path.isfile(filename) and not upgrade:
        logger.error(f'Language \'{alias}\' already exists. '
                     f'Use -U or --upgrade to override.')
    
    with open(filename, 'w') as file:
        file.write(config_text)
    print(f'Successfully installed \'{alias}\'.')

def uninstall(args: dict):
    language = args['<language>']
    lang_name = utils.lang_name(language)
    config_dir = get_config_dir()
    for filename in system_config_languages():
        file_lang = filename.split('.')[0]
        file_path = os.path.join(config_dir, filename)

        if filename == language or file_lang == language:
            os.remove(file_path)
            print(f'Successfully uninstalled \'{lang_name}\'.')
            return
    logger.warning(f'Skipping, \'{lang_name}\' not already installed.')

def get_symlink_args(filename, version) -> dict:
    # Stop initial args acting on the tool and not the language
    if not '--' in sys.argv:
        sys.argv.insert(1, '--')
    
    args = docopt(SYMLINK_CLI, version=version, options_first=True)

    if args['--where']:
        print(pathlib.Path(filename).resolve())
        exit(0)

    args['<language>'] = utils.lang_name(filename)
    base_args = args | {'<command>': 'run'}
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

    logger.verbose = base_args['--verbose'] or args['--verbose']
    logger.strict = base_args['--strict'] or args['--strict']

    globals()[base_args['<command>']](args)

import sys, os, fileinput, subprocess
from docopt import docopt
import networkx as nx
from tool.lexer import build_lexer
from tool.parser import build_parser, AST
import tool.utils as utils
from tool.utils import TaggedData
import tool.logger as logger
from tool.config import get_config, get_home_dir, get_config_text
from tool.constants import (
    CLI, SYMLINK_CLI, CLI_COMMANDS, NAME, VERSION, DEFAULT_REF
)


# class BiDict(UserDict):  
#     def __setitem__(self, key, item) -> None:
#         if self.__contains__(key):
#             self.pop(key)
#         if self.__contains__(item):
#             self.pop(item)
#         super().__setitem__(key, item)
#         super().__setitem__(item, key)
    
#     def __delitem__(self, key) -> None:
#         item = self.get(key)
#         super().__delitem__(key)
#         if key != item:
#             super().__delitem__(item)

# TODO updates break the normalised so should this really be its own class
# if it only does this at the start
# class NormalisedDict(UserDict):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.data = {
#             k:v if isinstance(v, list) else [v] 
#             for k,v in self.data.items()
#         }

class Functionality():
    def __init__(self, code: dict, commands: dict) -> None:
        tagged = {v[0]: v[1] for k, v in code.items() if type(v) == TaggedData}
        code = {k: v for k,v in code.items() if type(v) != TaggedData}

        self.tagged = utils.normalise_dict(tagged)
        self.code = utils.normalise_dict(code)
        self.commands = utils.normalise_dict(commands)

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

    def get_tagged(self, tag: str) -> str | None:
        return self.tagged.get(tag, None)

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

def requirements(req_file: str, reqs: str) -> None:
    if reqs == '':
        logger.warning('No requirements specified.')
    
    with open(req_file, 'w') as file:
        file.write(reqs)
    
    exit(0)

def link(args):
    # TODO Check <language> exists in .tool and not a path?
    lang_name = utils.lang_name(args['<language>'])
    dir = args['<dir>'] or os.getcwd()
    
    src = extension(sys.argv[0])
    dst = extension(os.path.join(dir, f'{lang_name}'))
    
    try:
        os.symlink(src, dst)
    except Exception as e:
        logger.error(f'Symbolic link error: {e}')

def run(args):
    language = args['<language>']
    lang_name = utils.lang_name(language)
    config = get_config(language)

    req_file = args['--requirements']
    if req_file:
        requirements(req_file, config.get('requirements', ''))

    version = config.get('version', None)
    usage = config.get('usage', None)
    
    inputs = args['<input>']

    # User language docopt
    if usage != None:
        language_args = docopt(usage, argv=inputs, version=version)
        # Requirement: Must specify single <input> in usage to be file parsed.
        src_input = language_args.get('<input>', None)
        if not(isinstance(src_input, str) or src_input == None):
            logger.error('File to be parsed must be specified in usage pattern' 
                         ' as \'<input>\' (file path), \'[<input>]\' '
                         '(file path or stdin) or nothing (stdin).')
    else:
        src_input = next(iter(inputs), None) # First element if it exists
    
    # Read input file if prsent else read from stdin
    with fileinput.input(files=src_input or ()) as file:
        src = ''.join(file)
    
    meta = config.get('meta', {})
    meta_tokens = meta.get('tokens', {})

    tokens = config['tokens']
    ignore = meta_tokens.get('ignore', ' \t')
    comment = meta_tokens.get('comment', None)
    using_regex = meta_tokens.get('regex', False)
    
    ref = meta_tokens.get('ref', DEFAULT_REF)
    if ref != False:
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
    grammar = config['grammar']
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
    tokens = {k: v for k, v in tokens.items() if k in tokens_in_grammar}
    token_map = {k: v for k, v in token_map.items() if k in tokens_in_grammar}
    symbol_map = token_map | grammar_map

    lexer = build_lexer(tokens, token_map, ignore, comment, using_regex)
    parser = build_parser(lang_name, list(token_map.values()), symbol_map, 
                          grammar, precedence)
    # lexer.input(src)
    # while True:
    #     tok = lexer.token()
    #     if not tok: 
    #         break      # No more input
    #     print(tok)

    ast = parser.parse(src, lexer=lexer)
    print(ast)
    code = config.get('code', {})
    commands = config.get('commands', {})
    functionality = Functionality(code, commands)

    global_env = {
        '__name__': lang_name,
        'args': language_args,
        #'ast': ast
    }
    before = functionality.get_tagged('before')
    if before:
        before = [cd for cd in before if cd != None]
        for cd in before: 
            exec(cd, global_env)
    
    #get_execute_func(ast, functionality, global_env)()
    
    # TODO  pass result of execution to after (or stdout if no after supplied)
    after = functionality.get_tagged('after')
    if after:
        after = [cd for cd in after if cd != None]
        for cd in after: 
            exec(cd, global_env)

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
            _ = local_env.get('_', None)
            return _
        elif cm:
            # TODO global and local vars TODO how to invoke code/command of child nonterminals
            env = os.environ.copy() | {}
            # TODO should stout/err be shown if run at root nonterminal?
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
    home_dir = get_home_dir()
    filename = os.path.join(home_dir, f'{alias}.yaml')
    
    if os.path.isfile(filename) and not upgrade:
        logger.error(f'Language \'{alias}\' already exists.')
    
    with open(filename, 'w') as file:
        file.write(config_text)
    print(f'Successfully installed {alias}.')

def uninstall(args: dict):
    language = args['<language>']
    lang_name = utils.lang_name(language)
    home_dir = get_home_dir()
    for filename in os.listdir(home_dir):
        file_lang = filename.split('.')[0]
        file_path = os.path.join(home_dir, filename)

        if filename == language or file_lang == language:
            os.remove(file_path)
            print(f'Successfully uninstalled {lang_name}.')
            return
    logger.warning(f'Skipping, {lang_name} not already installed.')

def get_symlink_args(command, version) -> dict:
    # Stop initial args acting on the tool and not the language
    if not '--' in sys.argv:
        sys.argv.insert(1, '--')
    
    args = docopt(SYMLINK_CLI, version=version, options_first=True)
    args['<language>'] = utils.base_name(command)
    args['run'] = True
    return args

def get_args(version):
    args = docopt(CLI, version=version, options_first=True)
    command = args['<command>']
    cli_command = CLI_COMMANDS.get(command, None)
    
    if command == 'help' or cli_command == None:
        print(CLI)
        exit(0)

    args |= docopt(cli_command, argv=args['<args>'], version=version, options_first=True)
    return args

def main():
    version = f'{NAME} {VERSION}'
    command = extension(sys.argv[0])
    
    if os.path.islink(command):
        args = get_symlink_args(command, version)
    else:
        args = get_args(version)

    logger.debug_mode = args.get('--debug', False)
    logger.strict_mode = args.get('--strict', False)

    globals()[args['<command>']](args)

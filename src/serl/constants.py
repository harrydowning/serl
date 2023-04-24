NAME = __package__
VERSION = '0.1.0-beta'

SYSTEM_CONFIG_DIR = f'.{NAME}'
SYSTEM_CONFIG_ENV_DIR = 'environments'
SHELL_CHAR = '$'
VENV_CONFIG = 'pyvenv.cfg'
EXCEPTION_ATTR = 'serl_loc'

OPTIONS = """Options:
    -h, --help     Show this screen.
    -V, --version  Show version.
    -v, --verbose  Provide more output."""

CLI = f"""{NAME}

Usage:
    {NAME} [options] <command> [<args>...]

Commands:
    link       Create a language symbolic link.
    install    install language to {SYSTEM_CONFIG_DIR} in home directory.
    uninstall  Uninstall language from {SYSTEM_CONFIG_DIR} in home directory.
    list       list installed languages.
    run        Execute language.
    help       Show help for commands.

{OPTIONS}"""

CLI_LINK = f"""{NAME} link

Usage:
    link [options] <language> [<dir>]

{OPTIONS}"""

CLI_INSTALL = f"""{NAME} install

Usage:
    install [options] <language> [(as <alias>)]

Install Options:
    -U, --upgrade  Override installed language if present.

{OPTIONS}"""

CLI_UNINSTALL = f"""{NAME} uninstall

Usage:
    uninstall [options] [<language>...]
    uninstall [options] --venv [<env>...]

{OPTIONS}"""

CLI_LIST = f"""{NAME} list

Usage:
    list [options]

List Options:
    --venv  List installed virtual environments.

{OPTIONS}"""

RUN_OPTIONS = f"""Run Options:
    -r, --requirements            Install pip requirements.
    --debug-lexer                 Output tokens found line-by-line.
    --debug-parser=FILE           Create parser state file.
    -H, --highlight=FILE          Create highlighted version of <src> in the 
                                  format of the extension of FILE.
    -f, --format=FORMAT           Override file extension format.
    -O, --format-options=OPTIONS  Options supplied to formatter.
    --style-defs=FILE             Output highlight style defs to FILE.
    --style-defs-arg=ARG          Argument supplied to style-defs."""

CLI_RUN = f"""{NAME} run

Usage:
    run [options] <language> [<args>...]

{RUN_OPTIONS}

{OPTIONS}"""

SYMLINK_CLI = f"""{NAME}

Usage:
    (language) [options] -- [<args>...]

Symlink Options:
    --where  Show symlink src location.

{RUN_OPTIONS}

{OPTIONS}"""

CLI_HELP = f"""{NAME} help

Usage:
    help [<command>]"""

CLI_COMMANDS = {
    'link': CLI_LINK,
    'install': CLI_INSTALL,
    'uninstall': CLI_UNINSTALL,
    'list': CLI_LIST,
    'run': CLI_RUN,
    'help': CLI_HELP
}

DEFAULT_REF = r'^token(?= )|(?<= )token(?= )|(?<= )token$'

PLY_ERR_MSG = {
    # lex 3.11 errorlog messages
    r".*:\d+: No regular expression defined for rule ('.*?')":
        r"No regular expression defined for rule \1",
    r".*:\d+: Regular expression for rule ('.*?') matches empty string": 
        r'Regular expression for token \1 matches empty string',
    r"Invalid regular expression for rule ('.*?').(.*?)": 
        r'Invalid regular expression for token \1:\2',
    
    r".*:\d+: Invalid regular expression for rule ('.*?').(.*)": 
        r'Invalid regular expression for token \1:\2',
    r".*:\d+. Make sure '#' in rule ('.*?') is escaped with '\\#'": 
        r"Make sure '#' in token \1 is escaped with '\#'",
    
    # yacc 3.11 errorlog messages
    r".*:\d+: Symbol ('.*?') used, but not defined as a token or a rule": 
        r'Symbol \1 used, but not defined as a token or a rule',
    r".*:\d+: Rule ('.*?') defined, but not used": 
        r'Rule \1 defined, but not used',
    
    # yacc 3.11 GrammarErrors
    r".*:\d+: Illegal name ('.*?') in rule '.*?'": 
        r'Symbol \1 used, but not defined as a token or rule'
}
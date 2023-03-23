NAME = __package__
VERSION = '0.0.1'

SYSTEM_CONFIG_DIR = f'.{NAME}'
OPTIONS = """Options:
    -h, --help     Show this screen.
    -V, --version  Show version.
    -v, --verbose  Provide more ouput.
    --strict       Run in strict mode, stopping execution on warnings."""

CLI = f"""{NAME}

Usage:
    {NAME} [options] <command> [<args>...]

Commands:
    link       Create a language symbolic link.
    install    install language to {SYSTEM_CONFIG_DIR} in home directory.
    uninstall  Uninstall language from {SYSTEM_CONFIG_DIR} in home directory.
    run        Execute language.
    help       Show command help screen. If non specified show this screen.

{OPTIONS}"""

CLI_LINK = f"""{NAME} link

Usage:
    link [options] <language> [<dir>]

{OPTIONS}"""

CLI_INSTALL = f"""{NAME} install

Usage:
    install [options] <language> [as <alias>]

Install Options:
    -U, --upgrade  Override installed language if present.

{OPTIONS}"""

CLI_UNINSTALL = f"""{NAME} uninstall

Usage:
    uninstall [options] <language>

{OPTIONS}"""

RUN_OPTIONS = f"""Run Options:
    -r, --requirements <file>  Create pip requirements file.
    --debug <file>             Create parser state debug file.
    --highlight <format>       Highlight <src> file in the specified format."""

CLI_RUN = f"""{NAME} run

Usage:
    run [options] <language> [<args>...]

{RUN_OPTIONS}

{OPTIONS}"""

SYMLINK_CLI = f"""{NAME}

Usage:
    (language) [[options] --] [<args>...]

{RUN_OPTIONS}

{OPTIONS}"""

CLI_HELP = f"""{NAME} help

Usage:
    help [<command>]"""

CLI_COMMANDS = {
    'link': CLI_LINK,
    'install': CLI_INSTALL,
    'uninstall': CLI_UNINSTALL,
    'run': CLI_RUN,
    'help': CLI_HELP
}

DEFAULT_REF = r'^token(?!$)|(?<= )token'

PLY_ERR_MSG = {
    # lex 3.11 errorlog messages
    '%s:%d: Regular expression for rule \'%s\' matches empty string': 
        ('Regular expression for token \'%s\' matches empty string', [2]),
    'Invalid regular expression for rule \'%s\'. %s': 
        ('Invalid regular expression for token \'%s\'.', [0]),
    '%s:%d: Invalid regular expression for rule \'%s\'. %s': 
        ('Invalid regular expression for token \'%s\'.', [2]),
    '%s:%d. Make sure \'#\' in rule \'%s\' is escaped with \'\\#\'': 
        ('Make sure \'#\' in token \'%s\' is escaped with \'\\#\'', [2]),
    
    # yacc 3.11 errorlog messages
    '%s:%d: Symbol %r used, but not defined as a token or a rule': 
        ('Symbol %r used, but not defined as a token or a rule', [2]),
    '%s:%d: Rule %r defined, but not used': 
        ('Rule %r defined, but not used', [2]),
}
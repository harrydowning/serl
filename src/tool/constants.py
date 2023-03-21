NAME = 'tool'
VERSION = '0.0.1'
SYSTEM_CONFIG_DIR = f'.{NAME}'

OPTIONS = f"""
Options:
  -h --help               Show this screen.
  -v --version            Show version.
  -r --requirements=FILE  Create pip requirements file.
  --debug                 Run in debug mode, logging runtime information.
  --strict                Run in strict mode, stopping evaluation on warnings.
"""

CLI = f"""{NAME}

Usage:
  {NAME} link <language> [<dir>]
  {NAME} install <language> [as <alias>]
  {NAME} uninstall <language>
  {NAME} [options] <language> [<input>]...
{OPTIONS}
"""

SYMLINK_CLI = f"""{NAME}

Usage:
  {NAME} [[options] --] [<input>]...
{OPTIONS}
"""

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
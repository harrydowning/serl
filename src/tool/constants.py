NAME = 'tool'
VERSION = '0.0.1'
SYSTEM_CONFIG_DIR = f'.{NAME}'

OPTIONS = f"""
Options:
  -h --help          Show this screen.
  -v --version       Show version.
  -r --requirements  Create pip requirements file.
  --debug            Run in debug mode, logging runtime information.
  --strict           Run in strict mode, stopping evaluation on warnings.
"""

CLI = f"""{NAME}

Usage:
  {NAME} link <language> [<dir>]
  {NAME} [options] <language> [<input>]...
{OPTIONS}
"""

SYMLINK_CLI = f"""{NAME}

Usage:
  {NAME} [[options] --] [<input>]...
{OPTIONS}
"""

DEFAULT_REF = r'^token(?!$)| token'
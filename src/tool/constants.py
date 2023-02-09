NAME = 'tool'
VERSION = '0.0.1'
SYSTEM_CONFIG_DIR = f'.{NAME}'
CLI = f"""{NAME}

Usage:
  {NAME} link <language> [<dir>]
  {NAME} [options] [(-l <language>)] [<input>]...

Options:
  -h --help               Show this screen.
  -v --version            Show version.
  --debug                 Run in debug mode, logging runtime information.
  --strict                Run in strict mode, stopping evaluation on warnings.
"""
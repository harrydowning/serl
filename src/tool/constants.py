NAME = 'tool'
VERSION = '0.0.1'
SYSTEM_CONFIG_DIR = f'.{NAME}'
LOCAL_CONFIG_FILE = f'config.yaml'
CLI = f"""{NAME}

Usage:
  {NAME} (link | unlink) <language>
  {NAME} [options] [(-l <language>)] [<input>]...

Options:
  -h --help               Show this screen.
  -v --version            Show version.
  --debug                 Run in debug mode.
  --strict                Run in strict mode. This stops evaluation at the
                          first warning.
"""
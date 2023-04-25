# Serialized Language (serl)
Serl is a command line tool used to manage and execute programming languages serialized with YAML.

Documentation can be found on [Read The Docs](https://serl.readthedocs.io/en/latest/user_guide/getting_started.html).

### Development Workflow
| Command | Description |
| ------- | ----------- |
| `pip install .` | Build/install locally |
| `serl help` | Show the tool command line help screen |
| `pytest tests` or `test.bat` | Run automated test suite |
| `py -m build` | Build distribution |
| `py -m twine upload dist/*` | Upload distribution |
| `sphinx-build -b html docs/source/ docs/build/html` | Build documentation |


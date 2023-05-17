# Serl - A tool for creating and using languages
<a href="https://pypi.org/project/serl/">
  <img src="https://img.shields.io/pypi/v/serl"/>
</a>
<a href="https://github.com/harrydowning/serl/blob/master/LICENSE">
  <img src="https://img.shields.io/github/license/harrydowning/serl"/>
</a>

Serl (serialized languages) is a format and corresponding command line tool for creating and using textual domain specific or markup languages with arbitrary syntax. This is achieved through the concept of language configurations, which are YAML files for specifying language syntax and functionality, used by the tool to execute language programs. These configurations can then be linked, allowing languages to be used like any other command line tool.

Documentation can be found on [Read The Docs](https://serl.readthedocs.io/en/latest/index.html).

### Development Workflow
| Command | Description |
| ------- | ----------- |
| `pip install .` | Build/install locally |
| `serl help` | Show the tool command line help screen |
| `pytest tests` or `test.bat` | Run automated test suite |
| `py -m build` | Build distribution |
| `py -m twine upload dist/*` | Upload distribution |
| `sphinx-build -b html docs/source/ docs/build/html` | Build documentation |


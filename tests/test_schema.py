import yaml
import tool.schema as schema
from tool.config import tagger
import pytest

test_data = [
    ("""
    version: string
    usage: string
    tokens:
        token: string
    grammar:
        rule: string
    code:
        rule: string
    """, True),
    ("""
    version: 1
    usage: string
    tokens:
        token: string
    grammar:
        rule: string
    code:
        rule: string
    """, True),
    ("""
    usage: string
    tokens:
        token: string
    grammar:
        rule: string
    code:
        rule: string
    """, True),
    ("""
    version: string
    tokens:
        token: string
    grammar:
        rule: string
    code:
        rule: string
    """, True),
    ("""
    tokens:
        token: string
    grammar:
        rule: string
    code:
        rule: string
    """, True),
    ("""
    tokens:
        _ignore: string
    grammar:
        rule: string
    code:
        rule: string
    """, True),
    ("""
    tokens:
        token: string
    grammar:
        rule: !tag string
    code:
        rule: string
    """, True),
    ("""
    tokens:
        token: string
    grammar:
        rule: !tag string
    commands:
        rule: string
    """, True),
    ("""
    version: string
    usage: string
    grammar:
        rule: string
    code:
        rule: string
    """, False),
    ("""
    version: string
    usage: string
    tokens:
        token: string
    code:
        rule: string
    """, False),
    ("""
    version: string
    usage: string
    tokens:
        token: string
    grammar:
        rule: string
    """, False),
]

@pytest.mark.parametrize("test_config, expected", test_data, 
                         ids=[f'config{i}' for i in range(len(test_data))])
def test_validate(test_config, expected):
    yaml.add_multi_constructor('!', tagger, Loader=yaml.SafeLoader)
    config = yaml.safe_load(test_config)
    valid, _ = schema.validate(config)
    assert valid == expected

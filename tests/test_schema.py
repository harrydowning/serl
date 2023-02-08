import yaml
import tool.schema as schema
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
    """, False)
]

@pytest.mark.parametrize("test_config,expected", test_data)
def test_schema(test_config, expected):
    config = yaml.safe_load(test_config)
    assert schema.validate(config) == expected

import yaml
import serl.schema as schema
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
    """, []),
    ("""
    version: 1
    usage: string
    tokens:
        token: string
    grammar:
        rule: string
    code:
        rule: string
    """, []),
    ("""
    usage: string
    tokens:
        token: string
    grammar:
        rule: string
    code:
        rule: string
    """, []),
    ("""
    version: string
    tokens:
        token: string
    grammar:
        rule: string
    code:
        rule: string
    """, []),
    ("""
    tokens:
        token: string
    grammar:
        rule: string
    code:
        rule: string
    """, []),
    ("""
    tokens:
        token: string
    grammar:
        rule: string
    code:
        rule: string
    Notes: string
    """, []),
    ("""
    version: string
    usage: string
    grammar:
        rule: string
    code:
        rule: string
    """, ['']),
    ("""
    version: string
    usage: string
    tokens:
        token: string
    code:
        rule: string
    """, ['']),
    ("""
    version: string
    usage: string
    tokens:
        token: string
    grammar:
        rule: string
    """, ['']),
    ("""
    version: string
    usage: string
    tokens:
        token: string
    grammar:
        rule: string
    code:
        rule: [1,2,3,4,5,6,7,8,9,10]
    """, [''] * 10),
]

@pytest.mark.parametrize("test_config, expected", test_data, 
                         ids=[f'config{i}' for i in range(len(test_data))])
def test_validate(test_config, expected):
    config = yaml.safe_load(test_config)
    errs = schema.validate(config)
    assert len(errs) == len(expected)

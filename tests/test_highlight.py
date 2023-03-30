import serl.highlight as highlight
import pytest

test_data = [
    ('key1=1, key2, key3=value3', 
     {'key1': 1, 'key2': True, 'key3': 'value3'}),
    ('key1="value1, key2", key3=value3, key4=\'key, value=\'', 
     {'key1': 'value1, key2', 'key3': 'value3', 'key4': 'key, value='}),
    ('key1=value1, key2', {'key1': 'value1', 'key2': True}),
    ('key1, key2, key3', {'key1': True, 'key2': True, 'key3': True}),
    ('key1=["list", "of", \'strings\'], key2=value2', 
     {'key1': ['list', 'of', 'strings'], 'key2': 'value2'})
]

@pytest.mark.parametrize("input, expected", test_data, 
                         ids=[f'input{i}' for i in range(len(test_data))])
def test_parse_key_value(input, expected):
    actual = highlight.parse_key_value(input)
    assert actual == expected


import pytest
import serl.parser as parser
from serl.parser import SerlAST

flipped_symbol_map = {
    'T0': 'a',
    'T1': 'b',
    'T2': 'c',
    'NT0': 'd',
    'NT1': 'e',
    'NT2': 'f'
}

@pytest.mark.parametrize('prod, p, expected', [
    (('NT0', 0, 'T1 NT1 T0 T1'), [None, '1', '2', '3', '4'] , 
     SerlAST('d', 0, {'b': ['1', '4'], 'e': ['2'], 'a': ['3']})),
    (('NT1', 1, 'T0 T1 T0 T2 T0 T1 T0'), [None, '1', '2', '3', '4', '5', '6', '7'] , 
     SerlAST('e', 1, {'a': ['1', '3', '5', '7'], 'b': ['2', '6'], 'c': ['4']})),
])
def test_get_prod_function(prod, p, expected):
    actual_prod = parser.get_prod_func(prod, flipped_symbol_map)
    assert actual_prod.__doc__ == f'{prod[0]} : {prod[2]}'
    actual_prod(p)
    actual_name, actual_i, actual_value = p[0]
    expected_name, expected_i, expected_value = expected
    assert actual_name == expected_name
    assert actual_i == expected_i
    assert actual_value == expected_value 
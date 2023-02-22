import tool.utils as utils

token_split = ['@', '']

tokens = {
    'text': r'([\w ]+)',
    'list': r'text(?:, @text)*',
    '*': r'\*',
    'row': r'@text \| @list',
    'rows': r'(@row \n)+'
}

repl_tokens = {
    '@text': r'([\w ]+)',
    '@list': r'text(?:, @text)*',
    '@\\*': r'\*',
    '@row': r'@text \| @list',
    '@rows': r'(@row \n)+'
}

exp_order = list(repl_tokens.keys()) # already in DAG order

sorted_repl_tokens = {
    '@text': r'([\w ]+)',
    '@list': r'text(?:, @text)*',
    '@rows': r'(@row \n)+',
    '@\\*': r'\*',
    '@row': r'@text \| @list'
}

exp_repl_tokens = {
    '@text': r'([\w ]+)',
    '@list': r'text(?:, ([\w ]+))*',
    '@\\*': r'\*',
    '@row': r'([\w ]+) \| text(?:, ([\w ]+))*',
    '@rows': r'(([\w ]+) \| text(?:, ([\w ]+))* \n)+'
}

exp_tokens = {
    'text': r'([\w ]+)',
    'list': r'text(?:, ([\w ]+))*',
    '*': r'\*',
    'row': r'([\w ]+) \| text(?:, ([\w ]+))*',
    'rows': r'(([\w ]+) \| text(?:, ([\w ]+))* \n)+'
}

def test_get_sorted_tokens():
    actual = list(utils.get_sorted_tokens(tokens).keys())
    expected = ['text', 'list', 'rows', 'row', '*']
    assert actual == expected

def test_get_repl_tokens():
    actual = utils.get_repl_tokens(tokens, token_split)
    expected = repl_tokens
    assert actual == expected

def test_get_token_graph():
    actual = sorted(utils.get_token_graph(repl_tokens))
    expected = sorted([('@text', '@list'), ('@text', '@row'), 
                       ('@list', '@row'), ('@row', '@rows')])
    assert actual == expected

def test_expand_tokens():
    actual = utils.expand_tokens(exp_order, repl_tokens)
    expected = exp_repl_tokens
    assert actual == expected

def test_token_expansion():
    actual = utils.token_expansion(tokens, token_split)
    expected = exp_tokens
    assert actual == expected
    # ensure order is also preserved
    assert list(actual.keys()) == list(expected.keys())

token_map = {
    '<': 'TOKEN0',
    '>': 'TOKEN1',
    'foo': 'TOKEN2',
    'foos': 'TOKEN3',
    'bar': 'TOKEN4'
}

grammar = {
    'MAIN': ['''
    <foo>
        OTHER
    <foos>
    ''', 'bar OTHER'],
    'OTHER': '<>'
}

norm_grammar = {
    'MAIN': ['TOKEN0 TOKEN2 TOKEN1 OTHER TOKEN0 TOKEN3 TOKEN1',
              'TOKEN4 OTHER'],
    'OTHER': ['TOKEN0 TOKEN1']
}

undef_norm_grammar = {
    'MAIN': ['TOKEN0 TOKEN2 TOKEN1 OTHER + ANOTHER TOKEN0 TOKEN3 TOKEN1',
              'TOKEN4 OTHER'], 
    'OTHER': ['TOKEN0 TOKEN1']
}

def test_normalise_grammar():
    actual = utils.normalise_grammar(token_map, grammar)
    expected = norm_grammar
    assert actual == expected

def test_undefined_symbol():
    actual = utils.get_undefined_symbols(token_map, undef_norm_grammar)
    expected = ['+', 'ANOTHER']
    assert sorted(actual) == sorted(expected)

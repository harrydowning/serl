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

def test_get_sorted_map():
    actual = list(utils.get_sorted_map(tokens).keys())
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

symbol_map = {
    '<': 'TERM0',
    '>': 'TERM1',
    'foo': 'TERM2',
    'foos': 'TERM3',
    'bar': 'TERM4',
    'MAIN': 'NONTERM0',
    'OTHER': 'NONTERM1'
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
    'NONTERM0': ['TERM0 TERM2 TERM1 NONTERM1 TERM0 TERM3 TERM1',
                 'TERM4 NONTERM1'],
    'NONTERM1': ['TERM0 TERM1']
}

undef_norm_grammar = {
    'NONTERM0': ['TERM0 TERM2 TERM1 NONTERM1 + ANOTHER TERM0 TERM3 TERM1',
                 'TERM4 NONTERM1'], 
    'NONTERM1': ['TERM0 TERM1']
}

def test_normalise_grammar():
    actual = utils.normalise_grammar(symbol_map, grammar)
    expected = norm_grammar
    assert actual == expected

# def test_undefined_symbol():
#     actual = utils.get_undefined_symbols(symbol_map, undef_norm_grammar)
#     expected = ['+', 'ANOTHER']
#     assert sorted(actual) == sorted(expected)

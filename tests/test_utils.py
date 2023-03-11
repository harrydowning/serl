import pytest
import tool.utils as utils
from tool.config import TaggedData

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

d = {
    'key1': 'value1',
    'key2': ['value21', 'value22']
}

def test_normalise_dict():
    actual = utils.normalise_dict(d)
    expected = d | {'key1': ['value1']}
    assert actual == expected

token_map = {
    '<': 'TERM0',
    '>': 'TERM1',
    'foo': 'TERM2',
    'foos': 'TERM3',
    'bar': 'TERM4',
    'extra': 'TERM5'
}

grammar_map = {
    'MAIN': 'NONTERM0',
    'OTHER': 'NONTERM1'
}

symbol_map = token_map | grammar_map

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

def test_normalise_grammar():
    actual = utils.normalise_grammar(symbol_map, grammar)
    expected = norm_grammar
    assert actual == expected

def test_get_tokens_in_grammar():
    actual = utils.get_tokens_in_grammar(token_map, norm_grammar)
    expected = ['<', '>', 'foo', 'foos', 'bar']
    assert actual == expected

obj = {
    'precedence': [TaggedData('nonassoc', '< >'), TaggedData('left', '+ -'), 
                   TaggedData('left', '* /')],
    'grammar': {
        'main': TaggedData('custom', '< items >'),
        'items': [TaggedData('list', 'items item'), 
                  TaggedData('list', 'item')],
        'other': TaggedData('all', ['first', 'second', 
                                    TaggedData('override', 'third')])
    }
}

obj_tagless = {
    'precedence': ['< >', '+ -', '* /'],
    'grammar': {
        'main': '< items >',
        'items': ['items item','item'],
        'other': ['first', 'second', 'third']
    }
}

obj_expanded = obj | {
    'grammar': {
        'main': TaggedData('custom', '< items >'),
        'items': [TaggedData('list', 'items item'), 
                  TaggedData('list', 'item')],
        'other': [TaggedData('all', 'first'), TaggedData('all','second'), 
                  TaggedData('override', 'third')]
    }
}

recurse_tags_data = [(obj, True, obj_tagless), (obj, False, obj_expanded)]

@pytest.mark.parametrize("obj, remove, expected", recurse_tags_data)
def test_recurse_tags(obj, remove, expected):
    actual = utils.recurse_tags(obj, remove=remove)
    assert actual == expected

code = {
    'p1': ['b1'],
    'p2': [None, 'b2'],
    'p3': [None, 'b3'],
    'p4': ['b4']
}

commands = {
    'p2': [None, 'b5'],
    'p3': ['b6'],
    'p4': ['b7'],
    'p5': ['b8']
}

def test_get_dups():
    actual = utils.get_dups(code, commands)
    expected = [('p2', 1), ('p4', 0)]
    assert sorted(actual) == sorted(expected)

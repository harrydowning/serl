import re
import serl.utils as utils
import pytest

id = lambda x: x
@pytest.mark.parametrize('rule,  symbol_map, symbol_f, repl_f, expected', [
    ('<a>', [('<', 'b'), ('>', 'b')], id, lambda x: f' {x} ', ' b a b '),
    ('a * a', [('*', 'b')], re.escape, id, 'a b a'),
    ('b aaab', [('a+', 'c'), ('b$', 'd')], id, id, 'b cd'),
    ('b aaab', [('a+?', 'c'), ('b$', 'd')], id, id, 'b cccd'),
    ('aba', [('a', 'b'), ('bbb', 'c')], id, id, 'bbb')
])
def test_expand(rule, symbol_map, symbol_f, repl_f, expected):
    actual = utils.expand(rule, symbol_map, symbol_f, repl_f)
    assert actual == expected

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

@pytest.mark.parametrize('token_map, error, norm_grammar, expected', [
    ({'num': 'TERMINAL0'}, None, {'NT0': ['NT0 + NT0', 'NT0 - NT0', '- NT0', 'TERMINAL0']}, 
     (['num'], {'+': 'ITERMINAL0', '-': 'ITERMINAL1'}, 
      {'NT0': ['NT0 ITERMINAL0 NT0', 'NT0 ITERMINAL1 NT0', 'ITERMINAL1 NT0', 'TERMINAL0']})),
    ({'num': 'TERMINAL0'}, 'err', {'NT0': ['NT0 + NT0', 'NT0 - NT0', '- err NT0', 'TERMINAL0']}, 
     (['num'], {'+': 'ITERMINAL0', '-': 'ITERMINAL1'}, 
      {'NT0': ['NT0 ITERMINAL0 NT0', 'NT0 ITERMINAL1 NT0', 'ITERMINAL1 error NT0', 'TERMINAL0']})),
])
def test_get_tokens_in_grammar(token_map, error, norm_grammar, expected):
    expected_used, expected_map, expected_grammar = expected

    actual_used, actual_map = utils.get_tokens_in_grammar(token_map, error, norm_grammar)
    assert actual_used == expected_used
    assert actual_map == expected_map
    assert expected_grammar == norm_grammar

def test_flip_dict():
    expected = utils.flip_dict({'key_str': 'value', 'key_num': 1})
    actual = {'value': 'key_str', 1: 'key_num'}
    assert actual == expected

@pytest.mark.parametrize('language, expected', [
    ('lang1.yaml', 'lang1'), ('lang2.yaml.yaml', 'lang2.yaml')
])
def test_get_language_name(language, expected):
    actual = utils.get_language_name(language)
    assert actual == expected

@pytest.mark.parametrize('d, l, expected', [
    ({'a': 1, 'b': 2, 'c': 3}, ['a', 'c'], {'a': 1, 'c': 3}), 
    ({'a': 1, 'b': 2, 'c': 3}, [], {})
])
def test_keep_keys_in_list(d, l, expected):
    actual = utils.keep_keys_in_list(d, l)
    assert actual == expected

@pytest.mark.parametrize('string, expected', [
    ('not-valid', 'notvalid'), ('90notvalid.txt', 'notvalidtxt')
])
def test_get_valid_identifier(string, expected):
    actual = utils.get_valid_identifier(string)
    assert actual == expected

@pytest.mark.parametrize('code, expected', [
    ({'init': ['c1', 'c2'], 'MAIN': ['c3'], 'OTHER': ['c4']}, ('init', ['c1', 'c2'])),
    ({'MAIN': ['c2'], 'OTHER': ['c3']}, None),
    ({'MAIN': ['c1'], 'init': ['c2'], 'OTHER': ['c3']}, None)
])
def test_get_main_code(code, expected):
    actual = utils.get_main_code(code,  grammar_map)
    assert actual == expected

import re
from typing import Callable
from tool.config import TaggedData

def expand(rule: str, symbol_map: list[tuple[str, str]], 
           symbol_f: Callable[[str], str] = lambda x: x, 
           repl_f: Callable[[str], str] = lambda x: x):
    if symbol_map == []:
        return rule
    symbol, repl = symbol_map[0]
    return repl_f(repl).join([expand(s, symbol_map[1:], symbol_f, repl_f) 
                             for s in re.split(symbol_f(symbol), rule)])

def get_sorted_map(tokens: dict[str, str]) -> dict[str, str]:
    sorted_tokens = {}
    for key in sorted(tokens, key=len, reverse=True):
        sorted_tokens[key] = tokens[key]
    return sorted_tokens

def get_repl_tokens(tokens: dict[str, str], split: list[str]) -> dict[str, str]:
    repl_tokens = tokens.copy()
    for token_def in tokens:
        # Using the fact that str.join is the inverse of str.split
        repl_token_def = re.escape(token_def).join(split)
        repl_tokens[repl_token_def] = repl_tokens.pop(token_def)
    return repl_tokens

def get_token_graph(repl_tokens: dict[str, str]) -> list[tuple[str, str]]:
    sorted_repl_tokens = get_sorted_map(repl_tokens)
    edges = set()
    for token_def in repl_tokens:
        splits = [repl_tokens[token_def]]
        for token_ref in sorted_repl_tokens:
            for i, split in enumerate(splits):
                if re.search(token_ref, split):
                    edges.add((token_ref, token_def))
                splits[i] = re.split(token_ref, split)
            splits = [s for split in splits for s in split]
    return list(edges)

def expand_tokens(exp_order: list[str], repl_tokens: dict[str, str]):
    exp_repl_tokens = repl_tokens.copy()
    for exp_tok in exp_order:
        sorted_repl_tokens = list(get_sorted_map(exp_repl_tokens).items())
        exp_repl_tokens[exp_tok] = expand(exp_repl_tokens[exp_tok], 
                                          sorted_repl_tokens)
    return exp_repl_tokens

def normalise_dict(d: dict) -> dict[str, list[str]]:
    d = recurse_tags(d, remove=True)
    return {k:v if type(v) == list else [v] for k,v in d.items()}

def normalise_grammar(symbol_map: dict[str, str],
                      grammar: dict) -> dict[str, list[str]]:
    sorted_map = list(get_sorted_map(symbol_map).items())
    norm_grammar = {}
    for nt, rules in normalise_dict(grammar).items():       
        for i, rule in enumerate(rules):
            exp_rule = expand(rule, sorted_map, re.escape, lambda x: f' {x} ')
            rules[i] = re.sub(r'\s+', ' ', exp_rule).strip()
        norm_grammar[symbol_map[nt]] = rules
    return norm_grammar

def get_tokens_in_grammar(token_map: dict[str, str], 
                          norm_grammar: dict[str, list[str]]) -> list[str]:
    tokens = list(token_map.values())
    rules = [rule for rules in norm_grammar.values() for rule in rules]
    used = set()
    for rule in rules:
        for token in tokens:
            if re.search(fr'\b{token}\b', rule):
                rule = re.sub(fr'\b{token}\b', '', rule)
                used.add(token)
    return [token for token, token_name in token_map.items() 
            if token_name in used]

def recurse_tags(obj, tag=None, remove=False):
    if isinstance(obj, dict):
        return {k: recurse_tags(v, tag, remove) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [recurse_tags(v, tag, remove) for v in obj]
    elif isinstance(obj, TaggedData):
        return recurse_tags(obj[1], obj[0], remove)
    else:
        return obj if tag == None or remove else TaggedData(tag, obj) 

def get_dups(d1: dict[str, list[str]], 
             d2: dict[str, list[str]]) -> list[tuple[str, int]]:
    dups = []
    for k, v1 in d1.items():
        v2 = d2.get(k, None)
        if v2:
            l = min(len(v1), len(v2))
            v1, v2 = v1[:l], v2[:l]
            dups += [(k, i) for i in range(l) 
                     if type(v1[i]) == type(v2[i]) and type(v1[i]) == str]
    return dups

def flip_map(d: dict) -> dict:
    return {v: k for k, v in d.items()}

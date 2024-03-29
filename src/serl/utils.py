import re
import os
from typing import Callable, Iterable
import serl.logger as logger

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
    return {k:v if type(v) == list else [v] for k,v in d.items()}

def expand_grammar_rule(rule, sorted_symbol_map):
    exp_rule = expand(rule, sorted_symbol_map, re.escape, lambda x: f' {x} ')
    return re.sub(r'\s+', ' ', exp_rule).strip()

def normalise_grammar(symbol_map: dict[str, str],
                      grammar: dict) -> dict[str, list[str]]:
    sorted_symbol_map = list(get_sorted_map(symbol_map).items())
    norm_grammar = {}
    for nt, rules in normalise_dict(grammar).items():       
        for i, rule in enumerate(rules):
            rules[i] = expand_grammar_rule(rule, sorted_symbol_map)
        norm_grammar[symbol_map[nt]] = rules
    return norm_grammar

def get_tokens_in_grammar(token_map: dict[str, str], error: str,
                          norm_grammar: dict[str, list[str]]):
    tokens = list(token_map.values())
    nonterms = norm_grammar.keys()
    flipped_token_map = flip_dict(token_map)
    
    tokens_used, implicit_map = set(), dict()
    for nt, rules in norm_grammar.items():
        for i, rule in enumerate(rules):
            new_rule = ''
            symbols = rule.split(' ')
            for j, symbol in enumerate(symbols):
                if symbol in tokens:
                    tokens_used.add(flipped_token_map[symbol])
                elif symbol in nonterms:
                    pass
                elif symbol == error:
                    if j == len(symbols) - 1:
                        logger.error(f'Error token \'{symbol}\' appears at the'
                                     f' end of a production.', code=1)
                    symbol = 'error'
                else:
                    if not implicit_map.get(symbol, None):
                        implicit_map[symbol] = f'ITERMINAL{len(implicit_map)}'
                    symbol = implicit_map[symbol]
                new_rule += f'{symbol} '
            norm_grammar[nt][i] = new_rule.strip()
    # Order implicit tokens by length
    return list(tokens_used), get_sorted_map(implicit_map)

def flip_dict(d: dict) -> dict:
    return {v: k for k, v in d.items()}

def get_language_name(language: str):
    name, ext = os.path.splitext(os.path.basename(language))
    return name

def keep_keys_in_list(d: dict, i: Iterable):
    return {k: v for k, v in d.items() if k in i}

def get_valid_identifier(s: str):
   s = re.sub('[^0-9a-zA-Z_]', '', s)
   s = re.sub('^[^a-zA-Z_]+', '', s)
   return s

def get_main_code(
        code: dict[str, list[str]], grammar_map: dict[str, str]
    ) -> tuple[str, list[str]] | None:
    item = next(iter(code.items()), None)
    if item[0] in grammar_map:
        return None
    else:
        return item

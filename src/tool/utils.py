import re

def expand(rule: str, symbol_map: list[tuple[str, str]], f = lambda x: x, pad = 0):
    if symbol_map == []:
        return rule
    symbol, repl = symbol_map[0]
    repl = f'{" " * pad}{repl}{" " * pad}'
    return repl.join([expand(s, symbol_map[1:], f, pad) 
                      for s in re.split(f(symbol), rule)])

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

def normalise_grammar(symbol_map: dict[str, str],
                      grammar: dict) -> dict[str, list[str]]:
    sorted_map = list(get_sorted_map(symbol_map).items())
    norm_grammar = {}
    for nt in grammar:
        if type(grammar[nt]) == str:
            rules = [grammar[nt]]
        else:
            rules = grammar[nt].copy()
        
        for i, rule in enumerate(rules):
            rules[i] = re.sub(r'\s+', ' ', expand(rule, sorted_map, re.escape, pad = 1)).strip()
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

# def get_undefined_symbols(token_map: dict[str, str], 
#                           norm_grammar: dict[str, list[str]]) -> list[str]:
#     nonterms, terms = list(norm_grammar.keys()), list(token_map.values())
#     symbols = sorted(nonterms + terms, key=len, reverse=True)
#     rules = [rule for rules in norm_grammar.values() for rule in rules]
#     undefined = []
#     for rule in rules:
#         for symbol in symbols:
#             rule = re.sub(fr'\b{symbol}\b', '', rule)
#         undefined += rule.strip().split(' ')
#     return [symbol for symbol in undefined if symbol != '' ]

# def check_undefined(token_map: dict[str, str], 
#                     norm_grammar: dict[str, list[str]]):
#     undefined = get_undefined_symbols(token_map, norm_grammar)
#     if len(undefined) > 0:
#         undef_list = ', '.join(f'\'{symbol}\'' for symbol in undefined)
#         logger.error(f'Undefined symbols used in grammar: {undef_list}.')

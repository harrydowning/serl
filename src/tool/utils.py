import re, copy
import networkx as nx
import tool.logger as logger
from tool.constants import DEFAULT_REF

def get_sorted_tokens(tokens: dict[str, str]) -> dict[str, str]:
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
    repl_tokens = repl_tokens.copy()
    edges = []
    for token_def in repl_tokens:
        for token_ref in repl_tokens:
            if re.search(token_ref, repl_tokens[token_def]):
                edges.append((token_ref, token_def))
                # Replace token_ref with '' so substrings of it aren't added
                repl_tokens[token_def] = re.sub(token_ref, '', 
                                                repl_tokens[token_def])
    return edges

def expand_tokens(exp_order: list[str], repl_tokens: dict[str, str]):
    sorted_repl_tokens = get_sorted_tokens(repl_tokens)
    exp_repl_tokens = repl_tokens.copy()
    for exp_tok in exp_order:
        for repl_tok in sorted_repl_tokens:
            # Due to behaviour of sub need to double up escapes
            # See https://docs.python.org/3/library/re.html#re.sub
            repl = exp_repl_tokens[repl_tok].replace('\\', '\\\\')
            exp_repl_tokens[exp_tok] = re.sub(repl_tok, repl, 
                                              exp_repl_tokens[exp_tok])
    return exp_repl_tokens

def token_expansion(tokens: dict[str, str], split: list[str]) -> dict[str, str]:
    repl_tokens = get_repl_tokens(tokens, split)
    token_graph = nx.DiGraph(get_token_graph(repl_tokens))
    cycles = list(nx.simple_cycles(token_graph))

    if cycles:
        cycle_nodes = {node for cycle in cycles for node in cycle}
        token_graph.remove_nodes_from(cycle_nodes)
        token_map = dict(zip(repl_tokens.keys(), tokens.keys()))
        
        for i, cycle in enumerate(cycles):
            cycle = map(lambda tok: f'\'{token_map[tok]}\'', cycle)
            msg = (f'Cyclic reference involving {", ".join(cycle)}.'
                    ' Preceding token(s) will not be expanded.')
            logger.warning(msg)
            
            shown = i + 1 
            remaining = len(cycles) - shown
            if shown >= len(tokens) and remaining > 1:
                logger.warning(f'[{remaining} more cycles...]')
                break

    exp_order = list(nx.topological_sort(token_graph))
    exp_tokens = expand_tokens(exp_order, repl_tokens)
    return dict(zip(tokens.keys(), exp_tokens.values()))

def normalise_grammar(token_map: dict[str, str],
                      grammar: dict) -> dict[str, list[str]]:
    grammar = copy.deepcopy(grammar)
    for nt in grammar:
        rules = grammar[nt]
        if type(rules) == str:
            rules = [rules]
            grammar[nt] = rules
        
        for i, _ in enumerate(rules):
            sorted_map = get_sorted_tokens(token_map)
            for token in sorted_map:
                rules[i] = rules[i].replace(token, f' {sorted_map[token]} ')
            rules[i] = re.sub(r'\s+', ' ', rules[i]).strip()
    return grammar

def get_tokens_in_grammar(token_map: dict[str, str], 
                          norm_grammar: dict[str, list[str]]) -> list[str]:
    tokens = sorted(token_map.values(), key=len, reverse=True)
    rules = [rule for rules in norm_grammar.values() for rule in rules]
    used = set()
    for rule in rules:
        for token in tokens:
            if token in rule:
                rule.replace(token, '')
                used.add(token)
    return [token for token, token_name in token_map.items() 
            if token_name in used]

def get_undefined_symbols(token_map: dict[str, str], 
                          norm_grammar: dict[str, list[str]]) -> list[str]:
    nonterms, terms = list(norm_grammar.keys()), list(token_map.values())
    symbols = sorted(nonterms + terms, key=len, reverse=True)
    rules = [rule for rules in norm_grammar.values() for rule in rules]
    undefined = []
    for rule in rules:
        for symbol in symbols:
            rule = re.sub(fr'\b{symbol}\b', '', rule)
        undefined += rule.strip().split(' ')
    return [symbol for symbol in undefined if symbol != '' ]

def check_undefined(token_map: dict[str, str], 
                    norm_grammar: dict[str, list[str]]):
    undefined = get_undefined_symbols(token_map, norm_grammar)
    if len(undefined) > 0:
        undef_list = ', '.join(f'\'{symbol}\'' for symbol in undefined)
        logger.error(f'Undefined symbols used in grammar: {undef_list}.')

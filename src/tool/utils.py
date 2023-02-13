import networkx as nx
from tool.logger import Logger

def get_sorted_tokens(tokens: dict[str, str]) -> dict:
    sorted_tokens = {}
    for key in sorted(tokens, key=len, reverse=True):
        sorted_tokens[key] = tokens[key]
    return sorted_tokens

def get_token_graph(tokens: dict[str, str]) -> list[tuple[str, str]]:
    tokens = tokens.copy()
    edges = []
    for token_def in tokens:
        for token_ref in tokens:
            if token_ref in tokens[token_def]:
                edges.append((token_ref, token_def))
                # Replace token_ref with '' so substrings of it aren't added
                tokens[token_def] = tokens[token_def].replace(token_ref, '')
    return edges

def expand_dict(d1: dict[str, str], d2: dict[str, str]) -> dict[str, str]:
    exp_d1 = d1.copy()
    for k1 in d1:
        for k2 in d2:
            exp_d1[k1] = exp_d1[k1].replace(k2, d2[k2])
    return exp_d1

def expand_tokens(exp_order: list[str], tokens: dict[str, str]):
    order_dict = {tok: tokens[tok] for tok in exp_order}
    sorted_tokens = get_sorted_tokens(tokens)
    return expand_dict(order_dict, sorted_tokens)

def expand_grammar(grammar: dict[str, str], tokens: dict[str, str]):
    sorted_tokens = get_sorted_tokens(tokens)
    return expand_dict(grammar, sorted_tokens)

def token_expansion(tokens: dict[str, str], logger: Logger) -> dict:
    token_graph = nx.DiGraph(get_token_graph(tokens))
    cycles = list(nx.simple_cycles(token_graph))

    if cycles:
        cycle_nodes = {node for cycle in cycles for node in cycle}
        token_graph.remove_nodes_from(cycle_nodes)

        for cycle in cycles:
            msg = (f"Cyclic reference in tokens: '{', '.join(cycle)}'."
                    " Tokens will not be expanded, check token definitions.")
            logger.warning(msg)

    exp_order = list(nx.topological_sort(token_graph))
    exp_tokens = expand_tokens(exp_order, tokens)
    # Return in original order
    return {tok: exp_tokens[tok] for tok in tokens}

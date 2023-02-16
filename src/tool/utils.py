import re
import networkx as nx
import tool.logger as logger

def get_sorted_tokens(tokens: dict[str, str]) -> dict[str, str]:
    sorted_tokens = {}
    for key in sorted(tokens, key=len, reverse=True):
        sorted_tokens[key] = tokens[key]
    return sorted_tokens

def get_repl_tokens(tokens: dict[str, str], 
                   start: str, end: str) -> dict[str, str]:
    repl_tokens = tokens.copy()
    for token_def in tokens:
        repl_token_def = start + re.escape(token_def) + end
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

def token_expansion(tokens: dict[str, str], 
                    start: str, end: str) -> dict[str, str]:
    repl_tokens = get_repl_tokens(tokens, start, end)
    token_graph = nx.DiGraph(get_token_graph(repl_tokens))
    cycles = list(nx.simple_cycles(token_graph))

    if cycles:
        cycle_nodes = {node for cycle in cycles for node in cycle}
        token_graph.remove_nodes_from(cycle_nodes)

        for cycle in cycles:
            msg = (f"Cyclic reference in tokens: '{', '.join(cycle)}'."
                    " These tokens will not be expanded.")
            logger.warning(msg)

    exp_order = list(nx.topological_sort(token_graph))
    exp_tokens = expand_tokens(exp_order, repl_tokens)
    return dict(zip(tokens.keys(), exp_tokens.values()))

# TODO remove tokens not used in grammar
# TODO warning/error if grammar contains tokens not defined

def get_grammar_tokens(grammar: dict[str, str], tokens: dict[str, str]) -> dict[str, str]:
    pass

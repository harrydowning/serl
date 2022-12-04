import os, io, pathlib
import yaml

def yaml_load_all(file: io.TextIOWrapper) -> dict:
    config = {}
    for i, doc in enumerate(yaml.safe_load_all(file)):
        if type(doc) != dict:
            continue
        # Note: If a language is named with an index it could be overriden
        name = doc.get('name', i)
        config[name] = doc
    return config

def get_system_config(filename: str) -> dict:
    home = os.path.expanduser('~')
    
    try:
        with open(os.path.join(home, filename)) as file:
            system_config = yaml_load_all(file)
    except FileNotFoundError:
        system_config = {}
    
    return system_config

def get_path_config(path: str | None) -> dict:
    if path == None:
        return {}
    
    # Note: may want this error to be shown to users
    try:
        with open(path) as file:
            path_config = yaml_load_all(file)
    except FileNotFoundError:
        path_config = {}

    return path_config

def get_local_config(filename: str) -> dict:
    local_path = None
    
    for path in pathlib.Path().rglob(filename):
        local_path = path
        break
    
    if local_path == None:
        return {}

    with open(local_path) as file:
        path_config = yaml_load_all(file)

    return path_config

# def get_inline_config(src: str) -> tuple[dict, str]:
#     with open(src) as file:
#         inline_config, content = list(yaml.safe_load_all(file))[:2]
#     return inline_config, content

def get_sorted_rules(rules: dict) -> dict:
    sorted_rules = {}
    for key in sorted(rules, key=len, reverse=True):
        sorted_rules[key] = rules[key]
    return sorted_rules

def get_rule_graph(rules: dict) -> list[tuple[str, str]]:
    rules = rules.copy()
    edges = []
    for def_rule in rules:
        for ref_rule in rules:
            if ref_rule in rules[def_rule]:
                edges.append((ref_rule, def_rule))
                # Replace ref_rule with '' so substrings of it aren't added
                rules[def_rule] = rules[def_rule].replace(ref_rule, '')
    return edges

def expand_rules(rule_order, rules):
    exp_rules = rules.copy()
    for def_rule in rule_order:
        for rule2 in rules:
            exp_rules[def_rule] = exp_rules[def_rule].replace(rule2, exp_rules[rule2])
    return exp_rules

def expand_patterns(patterns, rules):
    new_patterns = patterns.copy()
    for pattern in patterns:
        for rule in rules:
            new_patterns[pattern] = new_patterns[pattern].replace(rule, rules[rule])
    return new_patterns
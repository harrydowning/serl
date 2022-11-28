import yaml

def get_inline_config(src: str) -> tuple[dict, str]:
    with open(src) as file:
        loader = yaml.SafeLoader(file)
        inline_config = loader.get_data() # next(yaml.safe_load_all(file))
        print(loader.get_token())
    return inline_config

config = get_inline_config('test.txt')

print(config)

import yaml

with open('example.yaml', encoding='utf-8') as f:
    data = yaml.safe_load(f)

print(data)
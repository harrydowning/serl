import ply.lex as lex

tokens = (
    'SYNTAX',
    'RULE'
)

t_SYNTAX = r'.'

t_RULE = r'\{.*\}'

lexer = lex.lex()
data = """
[ {header}
  {text}
]
"""

lexer.input(data)

for token in lexer:
    print(token)
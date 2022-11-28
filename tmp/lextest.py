import ply.lex as lex
import regex

tokens = (
    'TEXT',
    'LINK',
    'OP'
    )

states = (
   ('link','exclusive'),
 )

# programatically adding variables
t_TEXT = r'[a-z]+'

t_ignore = r'''     
'''

def t_link(t):
    r'\['
    t.lexer.push_state('link')
    t.lexer.link = ()

def t_link_start(t):
    r'\['
    t.lexer.push_state('link')
    t.lexer.link = (*t.lexer.link, "[")

def t_link_text(t):
    r'[a-z ]+'
    t.lexer.link = (*t.lexer.link, t.value)
    pass
    
def t_link_end(t):
    r'\]'
    t.lexer.pop_state()
    if t.lexer.lexstate != 'link':
        t.value = t.lexer.link # t.lexer.lexdata[t.lexer.start:t.lexer.lexpos]
        t.type = 'LINK'
        return t
    t.lexer.link = (*t.lexer.link, "]")

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

#### Option One ####
# error = """
# def t_error(t):
#     print("Illegal character '%s'" % t.value[0])
#     t.lexer.skip(1)
# """
# exec(error)
#### Option One ####

def get_pattern_function(name, pattern):
    def f(t):
        s, e = t.lexer.lexmatch.span()
        string = t.lexer.lexmatch.string[s:e]
        m = regex.match(pattern, string, regex.VERBOSE)
        t.value = m.allcaptures()
        return t
    
    f.__doc__ = pattern
    return f

g = globals()
g['t_OP'] = get_pattern_function('t_OP', r'[\+\-\*\/]')


def build():
    return lex.lex()

lexer = build()

data = """
some text and a [link] with some other text

further text with a [nested [link [another nested]] lorem] like that [lorem [link] lorem]

"""

lexer.input('text + text - text * text / text')
for token in lexer:
    print(token)

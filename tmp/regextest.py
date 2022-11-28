import re
import regex

reg = r"""
(?: \[(\d+)\]: ([a-zA-Z0-9 ]*) \n+)? 
([a-zA-Z0-9 ]+) \n
---+ \n
(?:([a-zA-Z0-9 ]+) \| (\s*=* \*?) \s* (?| \[(\d+)\]  | ([a-zA-Z0-9 ]+) | ()) \n)+
"""

with open("test.txt") as file:
    input = file.read()


match = regex.match(reg, input, regex.VERBOSE)
print(dir(match))
print(match.capturesdict())
print(match.allcaptures()[1:])

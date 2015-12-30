from lexer import *

comment_start = Token("comment", "/*")
comment_end = Token("comment", "*/")
open_bracket = Token("bracket", "{")
close_bracket = Token("bracket", "}")
open_paren = Token("bracket", "(")
close_paren = Token("bracket" , ")")
open_sq_bracket = Token("bracket", "[")
close_sq_bracket = Token("bracket", "]")
equal = Token("assignment", "=")
semicolon = Token("semicolon", ";")
comma = Token("comma", ",")
minus = Token("addop", "-")
plus = Token("addop", "+")
aster = Token("asterisk", "*")
slash = Token("slash", "/")
percent = Token("percent", "%")
return_command = Token("command", "return")
int_type = Token("type", "int")

prims = [comment_start,
         comment_end,
         open_bracket,
         close_bracket,
         open_paren,
         close_paren,
         open_sq_bracket,
         close_sq_bracket,
         equal,
         semicolon,
         comma,
         minus,
         plus,
         aster,
         slash,
         percent,
         return_command,
         int_type]

prims_str = [prim.text for prim in prims]
prims_dict = dict(zip(prims_str, prims))

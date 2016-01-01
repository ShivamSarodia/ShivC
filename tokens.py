from lexer import *

comment_start = Token("comment", "/*")
comment_end = Token("comment", "*/")
plusplus = Token("crement", "++", 100)
minusminus = Token("crement", "--", 100)

plusequal = Token("assignment", "+=", 50)  # right-to-left
minusequal = Token("assignment", "-=", 50)
timesequal = Token("assignment", "*=", 50)
divequal = Token("assignment", "/=", 50)
modequal = Token("assignment", "%=", 50)

open_bracket = Token("bracket", "{")
close_bracket = Token("bracket", "}")
open_paren = Token("bracket", "(")
close_paren = Token("bracket" , ")")
open_sq_bracket = Token("bracket", "[", 100)
close_sq_bracket = Token("bracket", "]")
equal = Token("assignment", "=", 50) # right-to-left
semicolon = Token("semicolon", ";")
comma = Token("comma", ",")
minus = Token("addop", "-", 85)
plus = Token("addop", "+", 85)
aster = Token("asterisk", "*", 90)
slash = Token("slash", "/", 90)
percent = Token("percent", "%", 90)
return_command = Token("command", "return")
int_type = Token("type", "int")

prims = [comment_start,
         comment_end,
         plusplus,
         minusminus,

         plusequal,
         minusequal,
         timesequal,
         divequal,
         modequal,
         
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

assignment_ops = [prim for prim in prims if Token("assignment").match(prim)]

prims_str = [prim.text for prim in prims]
prims_dict = dict(zip(prims_str, prims))

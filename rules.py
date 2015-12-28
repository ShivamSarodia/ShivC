from rules_obj import *
from lexer import *

# This file might be broken up into multiple if it gets too unwieldy

### Symbols ###
S = Symbol("S")
statement = Symbol("statement")


### Rules ###
# After adding a rule, make sure to add it to the rules list at the bottom

main = Rule(S, [Token("type", "int"),
                Token("name", "main"),
                Token("("),
                Token(")"),
                Token("{"),
                statement,
                Token("}")])

return_form = Rule(statement, [Token("return"),
                               Token("integer"),
                               Token(";")])

rules = [main,
         return_form]

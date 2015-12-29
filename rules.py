from rules_obj import *
from lexer import *
import tokens

# This file might be broken up into multiple if it gets too unwieldy

### Symbols ###
S = Symbol("S")
statements = Symbol("statements")
statement = Symbol("statement")
math = Symbol("math")

### Rules ###
# After adding a rule, make sure to add it to the rules list at the bottom

main = Rule(S, [tokens.int_type,
                Token("name", "main"),
                tokens.open_paren,
                tokens.close_paren,
                tokens.open_bracket,
                statements,
                tokens.close_bracket])

statements_cont = Rule(statements, [statements,
                                    statement])

statements_end = Rule(statements, [statement])

return_form = Rule(statement, [tokens.return_command,
                               math,
                               tokens.semicolon])

math_num = Rule(math, [Token("integer")])

math_parens = Rule(math, [tokens.open_paren,
                          math,
                          tokens.close_paren])

# Note this covers both addition and subtraction
math_add = Rule(math, [math,
                       Token("addop"),
                       math])

math_mult = Rule(math, [math,
                        tokens.aster,
                        math])

math_div = Rule(math, [math,
                       tokens.slash,
                       math])

math_mod = Rule(math, [math,
                       tokens.percent,
                       math])

# Note this covers both +3 and -3
# Also, this rule needs to come after rule for regular addition
math_neg = Rule(math, [Token("addop"),
                       math])

rules = [main,
         statements_cont,
         statements_end,
         return_form,
         math_num,
         math_parens,
         math_add,
         math_mult,
         math_div,
         math_mod,
         math_neg]

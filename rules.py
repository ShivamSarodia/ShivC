from rules_obj import *
from lexer import *
import tokens

# This file might be broken up into multiple if it gets too unwieldy

### Symbols ###
S = Symbol("S")

main_setup = Symbol("main_setup")

statements = Symbol("statements")
statement = Symbol("statement")

math = Symbol("math")

declare_expression = Symbol("declare_expression");


### Rules ###
# After adding a rule, make sure to add it to the rules list at the bottom

main_setup_form = Rule(S, [main_setup,
                           tokens.open_paren,
                           tokens.close_paren,
                           tokens.open_bracket,
                           statements,
                           tokens.close_bracket])

main_setup_def = Rule(main_setup, [tokens.int_type,
                                   Token("name", "main")])

statements_cont = Rule(statements, [statements,
                                    statement])

statements_end = Rule(statements, [statement])

return_form = Rule(statement, [tokens.return_command,
                               math,
                               tokens.semicolon])

useless_declaration = Rule(statement, [Token("type"), tokens.semicolon])
real_declaration = Rule(statement, [declare_expression, tokens.semicolon])

base_declare = Rule(declare_expression, [Token("type"), Token("name")])
assign_declare = Rule(declare_expression, [declare_expression, tokens.equal, math])
cont_declare = Rule(declare_expression, [declare_expression, tokens.comma, Token("name")])

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

math_var = Rule(math, [Token("name")]) # important -- keep this below anything used for assignment

math_form = Rule(statement, [math, tokens.semicolon])

rules = [main_setup_form,
         main_setup_def,
         statements_cont,
         statements_end,
         return_form,
         useless_declaration,
         real_declaration,
         base_declare,
         assign_declare,
         cont_declare,
         math_num,
         math_parens,
         math_add,
         math_mult,
         math_div,
         math_mod,
         math_neg,
         math_var,
         math_form]

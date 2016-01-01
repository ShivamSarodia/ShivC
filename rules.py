from rules_obj import *
from lexer import *
import tokens

# This file might be broken up into multiple if it gets too unwieldy

### Symbols ###
S = Symbol("S")

main_setup = Symbol("main_setup")

statements = Symbol("statements")
statement = Symbol("statement")

E = Symbol("E")

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
                               E,
                               tokens.semicolon])



useless_declaration = Rule(statement, [Token("type"), tokens.semicolon])
real_declaration = Rule(statement, [declare_expression, tokens.semicolon])

base_declare = Rule(declare_expression, [Token("type"), Token("name")])
assign_declare = Rule(declare_expression, [declare_expression, tokens.equal, E], 49)
cont_declare = Rule(declare_expression, [declare_expression, tokens.comma, Token("name")])



E_num = Rule(E, [Token("integer")])
E_parens = Rule(E, [tokens.open_paren,
                    E,
                    tokens.close_paren])

E_add = Rule(E, [E,
                 Token("addop"),
                 E], 85)

E_mult = Rule(E, [E,
                  tokens.aster,
                  E], 90)

E_div = Rule(E, [E,
                 tokens.slash,
                 E], 90)

E_mod = Rule(E, [E,
                 tokens.percent,
                 E], 90)

E_eq_compare = Rule(E, [E,
                        Token("eq_compare"),
                        E], 70)

E_compare = Rule(E, [E,
                     Token("compare"),
                     E], 75)

E_neg = Rule(E, [Token("addop"),
                 E], 95)

E_equal = Rule(E, [Token("name"),
                   Token("assignment"),
                   E], 49) # 49 < 50, so it's right-associative now

E_inc_after = Rule(E, [Token("name"),
                       Token("crement")], 100)

E_inc_before = Rule(E, [Token("crement"),
                        Token("name")], 95)

# important -- keep this below any rules that should not reduce
E_var = Rule(E, [Token("name")])

E_form = Rule(statement, [E, tokens.semicolon])

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
         
         E_num,
         E_parens,
         E_add,
         E_mult,
         E_div,
         E_mod,
         E_eq_compare,
         E_compare,
         
         E_neg,
         E_equal,
         E_inc_after,
         E_inc_before,
         E_var,
         E_form]

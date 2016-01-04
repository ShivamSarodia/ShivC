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

declare_separator = Symbol("declare_separator")
declare_type = Symbol("declare_type")
declare_expression = Symbol("declare_expression");

if_start = Symbol("if_start");

if_statement = Symbol("if_statement");
else_statement = Symbol("else_statement");

### Rules ###
# After adding a rule, make sure to add it to the rules list at the bottom

main_setup_form = Rule(S, [main_setup,
                           tokens.open_paren,
                           tokens.close_paren,
                           tokens.open_bracket,
                           statements,
                           tokens.close_bracket])

main_setup_def = Rule(main_setup, [declare_type, # cuz the declaration is being weird. just go with it.
                                   Token("name", "main")])

statements_cont = Rule(statements, [statements,
                                    statement])

statements_end = Rule(statements, [statement])

return_form = Rule(statement, [tokens.return_command,
                               E,
                               tokens.semicolon])



useless_declaration = Rule(statement, [Token("type"), tokens.semicolon])
real_declaration = Rule(statement, [declare_expression, tokens.semicolon])

declare_type_base = Rule(declare_type, [Token("type")])
declare_type_cont = Rule(declare_type, [declare_type, tokens.aster])

declare_separator_base = Rule(declare_separator, [tokens.comma])
declare_separator_cont = Rule(declare_separator, [declare_separator, tokens.aster])

base_declare = Rule(declare_expression, [declare_type, Token("name")])
assign_declare = Rule(declare_expression, [declare_expression, tokens.equal, E], 49)
cont_declare = Rule(declare_expression, [declare_expression, declare_separator, Token("name")])



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

E_boolean_and = Rule(E, [E,
                         tokens.logic_and,
                         E], 65)

E_boolean_or = Rule(E, [E,
                        tokens.logic_or,
                        E], 60)

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

E_boolean_not = Rule(E, [tokens.logic_not, E], 95)

E_inc_after = Rule(E, [Token("name"),
                       Token("crement")], 100)

E_inc_before = Rule(E, [Token("crement"),
                        Token("name")], 95)

# important -- keep this below any rules that should not reduce
E_var = Rule(E, [Token("name")])

E_form = Rule(statement, [E, tokens.semicolon])

# We have to separate out the start so (E) doesn't reduce to E
if_start_form = Rule(if_start, [tokens.if_keyword,
                                tokens.open_paren])

if_form_empty = Rule(if_statement, [if_start,
                                    E,
                                    tokens.close_paren,
                                    tokens.semicolon])

if_form_brackets = Rule(if_statement, [if_start,
                                       E,
                                       tokens.close_paren,
                                       tokens.open_bracket,
                                       tokens.close_bracket])

if_form_oneline = Rule(if_statement, [if_start,
                                      E,
                                      tokens.close_paren,
                                      statements])
# it's OK to use statements above because statement -> statements immediately

if_form_main = Rule(if_statement,  [if_start,
                                    E,
                                    tokens.close_paren,
                                    tokens.open_bracket,
                                    statements,
                                    tokens.close_bracket])

else_form_empty = Rule(else_statement, [tokens.else_keyword,
                                        tokens.semicolon])

else_form_brackets = Rule(else_statement, [tokens.else_keyword,
                                           tokens.open_bracket,
                                           tokens.close_bracket])

else_form_oneline = Rule(else_statement, [tokens.else_keyword,
                                          statements])
# it's OK to use statements above because statement -> statements immediately

else_form_main = Rule(else_statement,  [tokens.else_keyword,
                                        tokens.open_bracket,
                                        statements,
                                        tokens.close_bracket])

# We use a priority here so if an "else" follows an "if_statement", the parser won't apply this rule
if_form_general = Rule(statement, [if_statement], 200)
ifelse_form_general = Rule(statement, [if_statement, else_statement])

rules = [main_setup_form,
         main_setup_def,
         statements_cont,
         statements_end,
         
         return_form,
         
         useless_declaration,
         real_declaration,
         declare_type_base,
         declare_type_cont,
         declare_separator_base,
         declare_separator_cont,
         base_declare,
         assign_declare,
         cont_declare,
         
         E_num,
         E_parens,
         E_add,
         E_mult,
         E_div,
         E_mod,
         E_boolean_and,
         E_boolean_or,
         E_eq_compare,
         E_compare,
         
         E_neg,
         E_equal,
         E_boolean_not,
         E_inc_after,
         E_inc_before,
         E_var,
         E_form,

         if_start_form,
         if_form_empty,
         if_form_brackets,
         if_form_oneline,
         if_form_main,
         if_form_general,
         
         else_form_empty,
         else_form_brackets,
         else_form_oneline,
         else_form_main,
         ifelse_form_general]

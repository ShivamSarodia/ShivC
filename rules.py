"""
The symbols and rules for the CFG of C. I generated these myself by hand, so
they're probably not perfectly correct.
"""

from rules_obj import *
from lexer import *
import tokens

### Symbols ###

# Most symbols are either self-explanatory, or best understood by examining the
# rules below to see how they're used.

S = Symbol("S")

main_setup = Symbol("main_setup") #TODO: is this neccesary?

# `statments` is a buch of `statement`s
statements = Symbol("statements")
# `statement` is a single C statement, semicolon included
statement = Symbol("statement")

# a generic expression
E = Symbol("E")

declare_separator = Symbol("declare_separator")
declare_type = Symbol("declare_type")
declare_expression = Symbol("declare_expression");
arr_start = Symbol("arr_start")
arr_end = Symbol("arr_end")
arr_list = Symbol("arr_list")

if_start = Symbol("if_start");
if_statement = Symbol("if_statement");
else_statement = Symbol("else_statement");

while_start = Symbol("while_start")
while_statement = Symbol("while_statement")

for_start = Symbol("for_start")
for1 = Symbol("for1")
for2 = Symbol("for2")
for3 = Symbol("for3")
for_expr =  Symbol("for_expr")

arg_start = Symbol("arg_start")
func_dec = Symbol("func_dec")
func_def = Symbol("func_def")

func_call_start = Symbol("func_call_start")

### Rules ###

# After adding a rule, make sure to add it to the rules list at the bottom!

# something that stands alone as a program, plus a function definition or
# declaration, can also stand alone as a program.
main_func_dec_cont = Rule(S, [S, func_dec])
main_func_def_cont = Rule(S, [S, func_def])
main_func_dec = Rule(S, [func_dec])
main_func_def = Rule(S, [func_def])

# make a `statements` symbol by extending another `statements` symbol
statements_cont = Rule(statements, [statements,
                                    statement])

# make a single `statement` symbol into a `statements` symbol
statements_end = Rule(statements, [statement])

# return statement
return_form = Rule(statement, [tokens.return_command,
                               E,
                               tokens.semicolon])

# a print statement
# The print statement is not valid C. I added it for ease of use, however, as
# I do not forsee this compiler being able to inclue stdio.h anytime soon.
print_form = Rule(statement, [tokens.print_command,
                              E,
                              tokens.semicolon])

# a declaration of the form int;
useless_declaration = Rule(statement, [Token("type"), tokens.semicolon])

# a declaration of the form `int a;` or `int a, b = 0;`
real_declaration = Rule(statement, [declare_expression, tokens.semicolon])

# the type part of a declaration, along with any pointers on the first variable
declare_type_base = Rule(declare_type, [Token("type")])
declare_type_cont = Rule(declare_type, [declare_type, tokens.aster])

# used to separate declarations. all these are declare_separators:
# ,
# ,*
# , **
#
declare_separator_base = Rule(declare_separator, [tokens.comma])
declare_separator_cont = Rule(declare_separator, [declare_separator, tokens.aster])

# the base of a declaration, like `int hello` or `int* hello`.
base_declare = Rule(declare_expression, [declare_type, Token("name")])
# a non-array declaration with an assignment, like `int hello = 4` or `int* hello = &p`.
assign_declare = Rule(declare_expression, [declare_expression, tokens.equal, E], 49)
# an array declaration with assignment, like `int hi[4] = {1, 2, 3, 4}`.
# Note--I imagine a better parser would catch things like `int hi = {1, 3}`.
# Mine, however, catches these errors at the code generation stage.
arr_assign_declare = Rule(declare_expression, [declare_expression, tokens.equal, arr_list], 49)
# Converts things like `int a, b` into a fresh declare_expression to chain declarations
cont_declare = Rule(declare_expression, [declare_expression, declare_separator, Token("name")])

# Defines `int a[5]` as a valid declare expression
array_num_declare = Rule(declare_expression, [declare_expression,
                                              tokens.open_sq_bracket,
                                              E,
                                              tokens.close_sq_bracket])
# Defines `int a[]` as a valid declare expression
array_nonum_declare = Rule(declare_expression, [declare_expression,
                                                tokens.open_sq_bracket,
                                                tokens.close_sq_bracket])
E_num = Rule(E, [Token("integer")])
E_parens = Rule(E, [tokens.open_paren,
                    E,
                    tokens.close_paren])

# Badly named--E_add can be binary addition or subtraction
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

# Again, badly named. E_neg can be either unary addition or subtraction
E_neg = Rule(E, [Token("addop"),
                 E], 95)

# Note this covers all of `a = 5`, `a *= 5`, `a /= 5`, etc.
# We give this rule a priority of 49, which is less than 50 (the priority) of
# the assignment symbols. This makes it right associative.
E_equal = Rule(E, [E,
                   Token("assignment"),
                   E], 49)

E_boolean_not = Rule(E, [tokens.logic_not, E], 95)

# Covers both a++ and a--
E_inc_after = Rule(E, [E,
                       Token("crement")], 100)

# Covers both ++a and --a
E_inc_before = Rule(E, [Token("crement"),
                        E], 95)

E_point = Rule(E, [tokens.aster, E], 95)
E_deref = Rule(E, [tokens.amper, E], 95)

# Calling a function like `f()`
E_func_noarg = Rule(E, [E, tokens.open_paren, tokens.close_paren])
# The start of a function call and first argument, like `f(1`
E_func_call_start = Rule(func_call_start, [E, tokens.open_paren, E], 0)
# Chaining more arguments onto the function call
E_func_call_cont = Rule(func_call_start, [func_call_start, tokens.comma, E], 0)
# Completing the function call
E_func_call_end = Rule(E, [func_call_start, tokens.close_paren])

# Array referencing, like `a[4]`
E_array = Rule(E, [E, tokens.open_sq_bracket, E, tokens.close_sq_bracket], 100)

E_var = Rule(E, [Token("name")])

E_form = Rule(statement, [E, tokens.semicolon])

# We have to separate out the start so (E) doesn't reduce to E in `if(E)`
if_start_form = Rule(if_start, [tokens.if_keyword,
                                tokens.open_paren])

# an if statement like `if(E) {}`
if_form_brackets = Rule(if_statement, [if_start,
                                       E,
                                       tokens.close_paren,
                                       tokens.open_bracket,
                                       tokens.close_bracket])
# a one line if statement like `if(E) a = 5;`
# it's OK to use "statements" here because statement -> statements immediately,
# so then this rule will apply right away

if_form_oneline = Rule(if_statement, [if_start,
                                      E,
                                      tokens.close_paren,
                                      statements])

# the most common if form, like `if(E) {a = 5;}`
if_form_main = Rule(if_statement,  [if_start,
                                    E,
                                    tokens.close_paren,
                                    tokens.open_bracket,
                                    statements,
                                    tokens.close_bracket])

# Same things, but for else
else_form_brackets = Rule(else_statement, [tokens.else_keyword,
                                           tokens.open_bracket,
                                           tokens.close_bracket])

else_form_oneline = Rule(else_statement, [tokens.else_keyword,
                                          statements])

else_form_main = Rule(else_statement,  [tokens.else_keyword,
                                        tokens.open_bracket,
                                        statements,
                                        tokens.close_bracket])

# We use a priority here so if an "else" follows an "if_statement", the parser
# won't apply the if_form_general rule (instead of the correct ifelse_form_general)
if_form_general = Rule(statement, [if_statement], 200)
ifelse_form_general = Rule(statement, [if_statement, else_statement])

break_form = Rule(statement, [tokens.break_keyword, tokens.semicolon])
cont_form = Rule(statement, [tokens.cont_keyword, tokens.semicolon])

# We have to separate out the start so (E) doesn't reduce to E
while_start_form = Rule(while_start, [tokens.while_keyword, tokens.open_paren])

# Same as if statement rules
while_form_brackets = Rule(statement, [while_start,
                                       E,
                                       tokens.close_paren,
                                       tokens.open_bracket,
                                       tokens.close_bracket])

while_form_oneline = Rule(statement, [while_start,
                                      E,
                                      tokens.close_paren,
                                      statements])

while_form_main = Rule(statement, [while_start,
                                   E,
                                   tokens.close_paren,
                                   tokens.open_bracket,
                                   statements,
                                   tokens.close_bracket])

# for statements
for_start_form = Rule(for_start, [tokens.for_keyword, tokens.open_paren])
for1_form = Rule(for1, [for_start, statements])
# The `statements` here better have a tree of the form: 
# statements -> statement -> E, semicolon
# A better parser would probably check this while parsing, but I check during
# code gen.
for2_form = Rule(for2, [for1, statements])
for_expr_form = Rule(for_expr, [for2, E, tokens.close_paren])
for_expr_form_empty = Rule(for_expr, [for2, tokens.close_paren])

# Same as if statement rules
for_form_empty = Rule(statement, [for_expr,
                                  tokens.semicolon])
for_form_brackets = Rule(statement, [for_expr,
                                     tokens.open_bracket,
                                     tokens.close_bracket])
for_form_oneline = Rule(statement, [for_expr,
                                    statements])
for_form_main = Rule(statement, [for_expr,
                                 tokens.open_bracket,
                                 statements,
                                 tokens.close_bracket])

# Array initializer with one element, like `{1}`
arr_list_one = Rule(arr_list, [tokens.open_bracket, E, tokens.close_bracket])
# Array initializer with no elements, like `{}`
arr_list_none = Rule(arr_list, [tokens.open_bracket, tokens.close_bracket])
# Start of array initializer and first element, like `{1,`
arr_list_start = Rule(arr_start, [tokens.open_bracket, E, tokens.comma])
# Contining array initalizer, like `{1, 2,`
arr_list_cont = Rule(arr_start, [arr_start, E, tokens.comma])
# Total array initializer, like `{1, 2, 3}`
arr_list_total = Rule(arr_list, [arr_start, arr_end])
# Array initializer end, like `3}`
arr_list_end = Rule(arr_end, [E, tokens.close_bracket])

# Argument list for defining/declaring functions
base_arg_form = Rule(arg_start, [declare_expression, # should have children [declare_type, name]
                                 tokens.open_paren,
                                 declare_expression])
cont_arg_form = Rule(arg_start, [arg_start,
                                 tokens.comma,
                                 declare_expression]) # should have kids [declare_type, name]
func_dec_form = Rule(func_dec, [arg_start, tokens.close_paren, tokens.semicolon])
func_def_form = Rule(func_def, [arg_start,
                                tokens.close_paren,
                                tokens.open_bracket,
                                statements,
                                tokens.close_bracket])

noarg_func_dec_form = Rule(func_dec, [declare_expression,
                                      tokens.open_paren,
                                      tokens.close_paren,
                                      tokens.semicolon])
noarg_func_def_form = Rule(func_def, [declare_expression,
                                      tokens.open_paren,
                                      tokens.close_paren,
                                      tokens.open_bracket,
                                      statements,
                                      tokens.close_bracket])

semicolon_form = Rule(statement, [tokens.semicolon])

# List of all the rules to apply. Applied in the listed order.
# In general, try to list rules above in the same order as they're listed here.

rules = [main_func_def_cont,
         main_func_dec_cont,
         main_func_def,
         main_func_dec,
         statements_cont,
         statements_end,
         return_form,
         print_form,
         
         useless_declaration,
         real_declaration,
         declare_type_base,
         declare_type_cont,
         declare_separator_base,
         declare_separator_cont,
         base_declare,
         assign_declare,
         arr_assign_declare,
         cont_declare,
         array_num_declare,
         array_nonum_declare,
         
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
         E_point,
         E_deref,
         E_func_noarg,
         E_func_call_start,
         E_func_call_cont,
         E_func_call_end,
         E_array,
         E_var,
         E_form,

         if_start_form,
         if_form_brackets,
         if_form_oneline,
         if_form_main,
         if_form_general,
         else_form_brackets,
         else_form_oneline,
         else_form_main,
         ifelse_form_general,

         break_form,
         cont_form,

         while_start_form,
         while_form_brackets,
         while_form_oneline,
         while_form_main,

         for_start_form,
         for1_form,
         for2_form,
         for_expr_form,
         for_expr_form_empty,
         for_form_brackets,
         for_form_oneline,
         for_form_main,

         arr_list_one,
         arr_list_none,
         arr_list_start,
         arr_list_cont,
         arr_list_total,
         arr_list_end,

         base_arg_form,
         cont_arg_form,
         func_dec_form,
         func_def_form,
         noarg_func_dec_form,
         noarg_func_def_form,
         
         semicolon_form]

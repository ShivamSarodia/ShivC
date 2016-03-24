"""
Parses the output of the lexer into a syntax tree. Currently uses a bottom-up
shift-reduce parsing algorithm. It's a touch ugly, but ShivC tries to avoid YACC
or the like.
"""

class ParseNode:
    """A node in the parse tree. Each node represents the application of a
    particular grammar rule to a list of children nodes. Both are attributes."""
    def __init__(self, rule, children):
        self.rule = rule
        self.children = children
    def __repr__(self):
        return str(self.rule.orig) + " -> " + str(self.children)
    def display(self, level = 0):
        """Used for printing out the tree"""
        print("|    " * level + str(self.rule.orig))
        for child in self.children:
            child.display(level+1)
    def bracket_repr(self): # http://ironcreek.net/phpsyntaxtree/?
        outstr = "[" + str(self.rule.orig) + " "
        outstr += ' '.join(child.bracket_repr() for child in self.children)
        outstr += "]"
        return outstr

class ParseException(Exception):
    """An exception raised if the parsing goes badly"""
    def __init__(self, stack):
        self.stack = stack
    def __str__(self):
        return "Error parsing input.\nEnd tree: " + str(self.stack)

def generate_tree(tokens, rules, start_symbol,
                  comment_start, comment_end,
                  add_rule, neg_rule,
                  mult_rule, pointer_rule,
                  dec_sep_rule, dec_exp_symbol):
    """Generates a syntax tree out of a list of tokens.

    rules - A list of rules to apply. See rules.py.
    start_symbol - The start symbol in the list of rules.
    comment_start/end - The symbols that start/end a comment
    add_rule - The binary +/- rule
    neg_rule - The unary +/- rule
    mult_rule - The binary multiplication rule
    pointer_rule - The pointer rule
    dec_sep_rule - The base declaration separator rule
    dec_exp_symbol - The symbol for a declaration"""
    
    # Remove comments from tokens
    # TODO: ignore comment_start and comment_end in strings
    comm_start = 0 # index at which comment starts
    in_comment = False
    for index, token in enumerate(tokens):
        if token == comment_start and not in_comment:
            in_comment = True
            comm_start = index
        if token == comment_end and in_comment:
            in_comment = False
            
             # remove tokens in the comment (replace with None)
            for i in range(comm_start, index+1): tokens[i] = None

    # `tokens` stores the list of remaining tokens to inject into stack
    # currently is is all tokens that aren't commented.
    tokens = [token for token in tokens if token]

    # stores the stack of symbols for the bottom-up shift-reduce parser
    stack = []
    # stores the tree itself in an analogous stack
    tree_stack = []

    # We keep looping until none of the rules apply anymore and there are no
    # more tokens to inject into the stack.
    while True:
        #print(stack) # great for debugging

        skip_neg = False # don't apply the unary +/- rule if binary +/- skipped
        skip_point = False # don't apply pointer rule if binary * skipped
        
        # Example of above:
        # If we have 3 + 4 * 5, we will skip applying add_rule to 3 + 4 because
        # * has higher priority. However, we then also need to skip applying the
        # unary + rule to the +4.
        
        for rule in rules:
            # The rule can't possibly match if there are more symbols to match
            # than there are symbols in the stack
            if len(rule.new) > len(stack): continue
            else:
                # check if the rule matches with the top of the stack
                for rule_el, stack_el in zip(reversed(rule.new), reversed(stack)):
                    # Break if any element of rule doesn't match the stack
                    if not rule_el.match(stack_el): break
                else:
                    # This rule matched!

                    # If the next token we'd inject has a higher priority than
                    # current rule, don't apply this rule

                    # Example: 3 + 4 * 5. When considering add_rule on 3 + 4, we
                    # should not apply this rule because we'll see tokens[0] is
                    # the asterisk, which has higher priority than the add rule.
                    if( rule.priority is not None
                        and len(tokens) > 0 and tokens[0].priority is not None
                        and tokens[0].priority > rule.priority ):

                        # If we skipped binary +/- for this reason, also skip unary +/-
                        # (see definitions of skip_neg and skip_point above)
                        if rule == add_rule: skip_neg = True
                        # If we skiped binary * for this reason, also skip pointer dereference
                        if rule == mult_rule: skip_point = True

                    # if we're supposed to skip unary +/-, do so
                    elif rule == neg_rule and skip_neg:
                        pass
                    # if we're supposed to skip unary *, do so
                    elif rule == pointer_rule and skip_point:
                        pass
                    # dirty hack to make declarations collapse right
                    # only reduce the comma if the previous symbol is a declare_expression
                    elif rule == dec_sep_rule and stack[-2] != dec_exp_symbol:
                        pass

                    else:
                        # we apply the rule!

                        # simplify the tree stack
                        tree_stack = tree_stack[:-len(rule.new)] + [ParseNode(rule, tree_stack[-len(rule.new):])]
                        # simplify the stack
                        stack = stack[:-len(rule.new)] + [rule.orig]
                        break # don't bother checking the rest of the rules
        else: # none of the rules matched
            # if we're all out of tokens, we're done
            if not tokens: break
            else: # inject another token into the stack
                stack.append(tokens[0])
                tree_stack.append(tokens[0])
                tokens = tokens[1:]
                
    # when we're done, we should have the start symbol left in the stack
    if stack == [start_symbol]:
        return tree_stack[0]
    else:
        raise ParseException(tree_stack)

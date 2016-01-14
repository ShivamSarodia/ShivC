# Currently uses a bottom-up shift-reduce parsing algorithm.
# I might improve this later on; I'm trying to avoid YACC or the like.

class ParseNode:
    def __init__(self, rule, children):
        self.rule = rule
        self.children = children
    def __repr__(self):
        return str(self.rule.orig) + " -> " + str(self.children)
    def display(self, level = 0):
        print("|    " * level + str(self.rule.orig))
        for child in self.children:
            child.display(level+1)
    def bracket_repr(self): # http://ironcreek.net/phpsyntaxtree/?
        outstr = "[" + str(self.rule.orig) + " "
        outstr += ' '.join(child.bracket_repr() for child in self.children)
        outstr += "]"
        return outstr

class ParseException(Exception):
    def __init__(self, stack):
        self.stack = stack
    def __str__(self):
        return "Error parsing input.\nEnd tree: " + str(self.stack)

def generate_tree(tokens, rules, start_symbol,
                  comment_start, comment_end,
                  add_rule, neg_rule,
                  mult_rule, pointer_rule,
                  dec_sep_rule, dec_exp_symbol):
    
    # Remove comments from tokens
    comm_start = 0
    in_comment = False
    for index, token in enumerate(tokens):
        if token == comment_start and not in_comment:
            in_comment = True
            comm_start = index
        if token == comment_end and in_comment:
            in_comment = False
            for i in range(comm_start, index+1): tokens[i] = None
    tokens = [token for token in tokens if token]

    stack = []
    tree_stack = []

    while True:
        #print(stack) # great for debugging
        skip_neg = False # don't apply negative rule if add_rule was skipped
        skip_point = False # don't apply pointer rule if mult_rule was skipped
        for rule in rules:
            if len(rule.new) > len(stack): continue
            else:
                for rule_el, stack_el in zip(reversed(rule.new), reversed(stack)): # does this rule match?
                    if not rule_el.match(stack_el): break # this element didn't match
                else:
                    # This rule matched
                    
                    if( rule.priority is not None
                        and len(tokens) > 0 and tokens[0].priority is not None
                        and tokens[0].priority > rule.priority ):  # if the next operation has a higher priority, skip it

                        # if we skipped the add rule, then also skip the negative rule
                        if rule == add_rule: skip_neg = True
                        if rule == mult_rule: skip_point = True

                    elif rule == neg_rule and skip_neg: # if we're supposed to skip the negative rule, do so
                        pass
                    elif rule == pointer_rule and skip_point: # if we're supposed to skip the pointer rule, do so
                        pass
                    elif rule == dec_sep_rule and stack[-2] != dec_exp_symbol:
                        # only reduce the comma if the previous symbol was declare_expression
                        pass

                    else:
                        tree_stack = tree_stack[:-len(rule.new)] + [ParseNode(rule, tree_stack[-len(rule.new):])]
                        stack = stack[:-len(rule.new)] + [rule.orig] # simplify the stack
                        break # don't bother checking the rest of the rules
        else: # none of the rules matched
            if not tokens: break
            else:
                stack.append(tokens[0])
                tree_stack.append(tokens[0])
                tokens = tokens[1:]
                
    # when we're done, we should have the start symbol
    if stack == [start_symbol]:
        return tree_stack[0]
    else:
        raise ParseException(tree_stack)

# Currently uses a bottom-up shift-reduce parsing algorithm.
# I might improve this later on; I'm trying to avoid YACC or the like.

class ParseNode:
    def __init__(self, rule, children):
        self.rule = rule
        self.children = children
    def __repr__(self):
        return str(self.rule.orig) + " -> " + str(self.children)

class ParseException(Exception):
    def __init__(self, stack):
        self.stack = stack
    def __str__(self):
        return "Error parsing input.\nEnd tree: " + str(self.stack)

def generate_tree(tokens, rules,
                  comment_start, comment_end,
                  add_rules, neg_rules, higher_than_add,
                  equal_rules, higher_than_equal,
                  name_reduce_rules, keep_as_name,
                  start_symbol):
    tokens = tokens[:] # so we can modify tokens

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
        skip_neg = False # don't apply negative rule if add_rule was skipped
        for rule in rules:
            if len(rule.new) > len(stack): continue
            #elif rule in add_rules and len(tokens) > 0 and tokens[0] in mult_tokens: continue
            # don't reduce if the next operation is multiplication
            else:
                for rule_el, stack_el in zip(reversed(rule.new), reversed(stack)): # does this rule match?
                    if not rule_el.match(stack_el): break # this element didn't match
                else: # this rule matched
                    if rule in add_rules and len(tokens) > 0 and tokens[0] in higher_than_add:
                        skip_neg = True #if the next operation has priority higher than adding, don't apply rule
                    elif rule in equal_rules and len(tokens) > 0 and tokens[0] in higher_than_equal:
                        pass #if the next operator has priority higher than equals, don't apply equal rule
                    elif rule in name_reduce_rules and len(tokens) > 0 and tokens[0] in keep_as_name:
                        pass #if the next operator is an assignment operator, keep this one as a name
                    elif rule in neg_rules and skip_neg: # skip the negative rule if we skipped add
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

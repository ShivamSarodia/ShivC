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
        return "Error parsing input"

def generate_tree(tokens, rules, start_symbol):
    tokens = tokens[:] # so we can modify tokens
    stack = []
    tree_stack = []

    while True:
        print(tree_stack)
        for rule in rules:
            if len(rule.new) > len(stack): continue
            else:
                for rule_el, stack_el in zip(reversed(rule.new), reversed(stack)): # does this rule match?
                    if not rule_el.match(stack_el): break # this element didn't match
                else: # this rule matched
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
        raise ParseException(stack)

"""
Stores the classes used to define rules for the parser.
"""

class Symbol:
    """A symbol in the CFG for C"""
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name
    def match(self, symbol):
        if not isinstance(symbol, Symbol): return False
        return (self.name == symbol.name)
        
class Rule:
    """A rule in the CFG for C"""
    def __init__(self, orig, new, priority = None):
        # orig - stores the symbol the rules replaces
        # new - stores the symbol(s) the rules replaces `orig` with
        # priority - priority of the rule relative to priority of nex
        self.orig = orig
        self.new = new
        self.priority = priority
    def __repr__(self):
        return str(self.orig) + " -> " + str(self.new)

    

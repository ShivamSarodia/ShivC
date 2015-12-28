class Symbol:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name
    def match(self, symbol):
        if not isinstance(symbol, Symbol): return False
        return (self.name == symbol.name)
        
class Rule:
    def __init__(self, orig, new, priority = 0):
        self.orig = orig
        self.new = new
        self.priority = priority
    def __repr__(self):
        return str(self.orig) + " -> " + str(self.new)

    

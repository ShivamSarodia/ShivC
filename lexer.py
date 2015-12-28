import re

class Token:
    def __init__(self, name, info = None):
        self.name = name
        self.info = info
    def match(self, token): # checks if token fits template made by self
        if not isinstance(token, Token): return False
        if self.name != token.name: return False
        if not self.info: return True
        return (self.info == token.info)
    def __repr__(self):
        return str(str(self.name) + ((" " + self.info) if self.info  else ""))

class TokenException(Exception):
    def __init__(self, bad_part):
        self.bad_part = bad_part
    def __str__(self):
        return "Error tokenizing part: " + self.bad_part
    
def tokenize(program):

    # A dictionary for the basic primitives
    prims = {"{":Token("{"),
             "}":Token("}"),
             "(":Token("("),
             ")":Token(")"),
             "[":Token("["),
             "]":Token("]"),
             ";":Token(";"),
             ",":Token(","),
             "-":Token("addop", "-"),
             "+":Token("addop", "+"),
             "return":Token("return"),
             "int":Token("type", "int")}

    parts = re.split("\s+", program) # split the original program by whitespace
    
    for prim in prims.keys(): # split by each of the primitives
        parts = sum([re.split("(" + re.escape(prim) + ")", part) for part in parts], [])
        parts = [p for p in parts if len(p) > 0]
            
    # For each element of parts, tokenize it.
    def make_token(part):
        if part in prims.keys(): # tokenize primitives
            return prims[part]
        elif re.fullmatch("[0-9]*", part): # tokenize integers
            return Token("integer", part)
        elif re.fullmatch("[a-zA-Z_][a-zA-Z0-9_]*", part): # tokenize valid names
            return Token("name", part)
        else: # we've found something unexpected! complain.
            raise TokenException(part)

    return list(map(make_token, parts))
            
    

    

        

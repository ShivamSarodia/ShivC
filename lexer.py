import re

class Token:
    def __init__(self, name, text = None):
        self.name = name
        self.text = text
    def match(self, token): # checks if token fits template made by self
        if not isinstance(token, Token): return False
        if self.name != token.name: return False
        if not self.text: return True
        return (self.text == token.text)
    def __eq__(self, other):
        return ((self.name == other.name) and (self.text == other.text))
    def __repr__(self):
        return str(str(self.name) + " " + str(self.text))

class TokenException(Exception):
    def __init__(self, bad_part):
        self.bad_part = bad_part
    def __str__(self):
        return "Error tokenizing part: " + self.bad_part
    
def tokenize(program, prims):

    parts = re.split("\s+", program) # split the original program by whitespace
    
    for prim in prims: # split by each of the primitives
        new_parts = []
        for part in parts:
            if isinstance(part, str):
                split = part.split(prim.text)
                for s in split:
                    if len(s) > 0: new_parts.append(s)
                    new_parts.append(prim)
                new_parts.pop()
            else:
                new_parts.append(part)
        parts = new_parts

    # For each remaining string element of parts, tokenize it.
    def make_token(part):
        if isinstance(part, Token):
            return part
        elif re.fullmatch("[0-9]*", part): # tokenize integers
            return Token("integer", part)
        elif re.fullmatch("[a-zA-Z_][a-zA-Z0-9_]*", part): # tokenize valid names
            return Token("name", part)
        else: # we've found something unexpected! complain.
            raise TokenException(part)

    return list(map(make_token, parts))
            
    

    

        

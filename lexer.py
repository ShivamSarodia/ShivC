"""
Lexer for ShivC. Converts a program string into a list of tokens.
"""

import re

class Token:
    """A token is a single semantic unit in C. See tokens.py for list of tokens
    that are defined."""
    def __init__(self, name, text = None, priority = None):
        # the general type of token (e.g. "assignment" or "bracket")
        self.name = name

        # usually the literal text of the token (e.g. "=" or "{")
        self.text = text

        # the parser does not apply a rule if the next token is higher priority
        # See the parser for more info.
        self.priority = priority

    def match(self, token):
        """Checks if the provided token matches self. Returns true iff both
        tokens have the same name and text, self.text is None"""
        if not isinstance(token, Token): return False
        if self.name != token.name: return False
        if not self.text: return True
        return (self.text == token.text)
    def __eq__(self, other):
        """Checks if two tokens are exactly equal in name and text"""
        return ((self.name == other.name) and (self.text == other.text))
    def __repr__(self):
        return str(str(self.name) + " " + str(self.text))
    def display(self, level = 0):
        """Debugging tool used to display tokens in a parse tree"""
        print("|    " * level + str(self))
    def bracket_repr(self):
        return self.text

class TokenException(Exception):
    """Exception thrown when a program cannot be split into tokens"""
    def __init__(self, bad_part):
        self.bad_part = bad_part
    def __str__(self):
        return "Error tokenizing part: " + self.bad_part
    
def tokenize(program, prims):
    """Executes the task of the lexer.
    program - the input program text, as a string
    prims - a list of the primitive tokens to split program into
    Returns a list of tokens representing the program.
    """

    # `parts` stores the current tokenization of the program
    # To begin, split the program by whitespace
    parts = re.split("\s+", program)
    
    # split by each of the primitives, in order
    for prim in prims:
        new_parts = [] # temporary storage for the next iteration of parts

        # for every part in current tokenization
        for part in parts:
            # if it isn't already a token, try splitting it up
            if isinstance(part, str):
                split = part.split(prim.text)

                # add results of spliting to new_parts
                for s in split:
                    if len(s) > 0: new_parts.append(s)
                    new_parts.append(prim)

                # we add one too many `prim`s above
                new_parts.pop()
                
            # if it's already a token, don't do anything
            else:
                new_parts.append(part)
                
        parts = new_parts

    # For each remaining string element of parts, tokenize it properly
    def make_token(part):
        # if it's already a token, don't change anything
        if isinstance(part, Token):
            return part
        # if it's a number, store it as an integer
        elif re.fullmatch("[0-9]*", part):
            return Token("integer", part)
        # if it's a valid name, stori it as a name
        elif re.fullmatch("[a-zA-Z_][a-zA-Z0-9_]*", part):
            return Token("name", part)
        else: # we've found something unexpected! complain.
            raise TokenException(part)

    return list(map(make_token, parts))
            
    

    

        

"""
The classes and exceptions used in the code generation phase.
"""

class RuleGenException(Exception):
    """If code generation fails for a particular rule"""
    def __init__(self, rule):
        self.rule = rule
    def __str__(self):
        return "Problem generating code for rule: " + str(self.rule)

# I guess this should be "redefinition" exception, technically
class VariableRedeclarationException(Exception):
    """If a variable is defined multiple times"""
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return "Variable declared multiple times: " + self.name

class VariableNotDeclaredException(Exception):
    """If a variable is not declared before it's used"""
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return "Variable not declared: " + self.name

class CodeManager:
    """Stores the generated code the parse tree is traversed. Also manages 
    labels for us intelligently."""
    def __init__(self):
        # Add all the starting boilerplate assembly
        self.setup = ["\tglobal start",
                      "",
                      "\tsection .text",
                      "",
                      "start:",
                      "\tmov rbp, rsp",
                      "\tlea rax, [rel retmain]",
                      "\tpush rax",
                      "\tpush rbp",
                      "\tmov rbp, rsp",
                      "", # on calling get_code, make this "\tjmp main_label"
                      "retmain:",
                      "\tpop rdi",
                      "\tmov rax, 0x2000001",
                      "\tsyscall"]
        self.lines = [] # stores the asm lines generated
        self.data = ["", "\tsection .data", "var:\tdb 0"]

        self.labelnum = 0 # current label number
    def get_code(self, main_label):
        """Actually generates the code by "linking" the main function. Returns a
        string containing the asm code"""
        self.setup[10] = "\tjmp " + main_label
        return '\n'.join(self.setup + self.lines + self.data)
    def add_command(self, comm, arg1 = "", arg2 = ""):
        """Adds a command to the list of current commands"""
        self.lines.append("\t"+ comm +
                          ((" " + arg1) if arg1 else "") +
                          ((", " + arg2) if arg2 else ""))
    def get_label(self):
        """Returns a string that is an unused label name"""
        label_name = "__label" + str(self.labelnum)
        self.labelnum += 1
        return label_name
        
    def add_label(self, label_name):
        """Adds a label with the provided name at the current position in the
        code"""
        self.lines.append(label_name + ":")

class Type:
    """The type of a value. Right now, only int and pointers to int are
    supported. Arrays are also supported, but dealt with elsewhere."""
    def __init__(self, type_name = "int", pointers = 0):
        self.type_name = type_name
        self.pointers = pointers
    def __repr__(self):
        return "*"*self.pointers + self.type_name
    def __eq__(self, other):
        return (self.type_name == other.type_name) and (self.pointers == other.pointers)

class StateInfo:
    """Manages the currently defined variables and functions and their locations
    in memory. Consider this class as being const--none of the methods modify
    the StateInfo object itself; rather, they return a modified `StateInfo`"""
    def __init__(self, var_offset = 0, symbols = [], funcs = [], t = Type()):
        # Amount of offset from rbp for last variable, divided by 8
        self.var_offset = var_offset
        self.symbols = symbols[:] # symbol table
        self.funcs = funcs[:] # function table
        
        # the type of the most thing returned by the most recent node
        # (see code_gen.py for more explanation)
        self.t = t
    def is_declared(self, name):
        """Whether a variable is declared"""
        return (name in [dec[0] for dec in self.symbols])
    def func_declared(self, func_name):
        """Whether a function is declared"""
        return (func_name in [func["fname"] for func in self.funcs])
    def add_space(self):
        """Returns a StateInfo object with 8 bytes of empty space added in
        memory representation"""
        s = self.c()
        s.var_offset += 1
        return s
    def add(self, name, t):
        """Returns a StateInfo object with a variable of name `name` and type 
        `t` added"""
        if self.is_declared(name): raise VariableRedeclarationException(name)
        else:
            s = self.c()
            s.var_offset += 1
            s.symbols += [(name, s.var_offset, t)]
            return s
    def get(self, name):
        """Returns the memory location and type of a variable"""
        var_loc = [var for var in self.symbols if var[0] == name]
        if var_loc:
            return (var_loc[0][1], var_loc[0][2])
        else:
            raise VariableNotDeclaredException(name)
    def add_func(self, func_name, func_type, func_args, label):
        """Returns a copy of StateInfo with a function added to the function table"""
        if self.func_declared(func_name): raise VariableRedeclarationException(func_name)
        else:
            s = self.c()
            s.funcs += [{"fname": func_name,
                         "ftype": func_type,
                         "args": func_args,
                         "label": label}] #TODO: complain if function is declared but never defined
            return s
    def get_func(self, func_name):
        """Returns details about the function `func_name`"""
        func_loc = [func for func in self.funcs if func["fname"] == func_name]
        if func_loc: return func_loc[0]
        else:
            raise VariableNotDeclaredException(func_name)
    def c(self):
        """Returns a copy of this object"""
        return StateInfo(self.var_offset, self.symbols, self.funcs, self.t)


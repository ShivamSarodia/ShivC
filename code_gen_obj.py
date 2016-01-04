class RuleGenException(Exception):
    def __init__(self, rule):
        self.rule = rule
    def __str__(self):
        return "Problem generating code for rule: " + str(self.rule)

class VariableRedeclarationException(Exception):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return "Variable declared multiple times: " + self.name

class VariableNotDeclaredException(Exception):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return "Variable not declared: " + self.name

class CodeManager:
    def __init__(self):
        self.setup = ["\tglobal start", "", "\tsection .text", "", "start:", "\tmov rbp, rsp"]
        self.lines = []
        self.data = ["\tmov rax, 0x2000001", "\tmov rdi, 0", "\tsyscall", "", "\tsection .data", "var:\tdb 0"]
        
        self.labelnum = 0
    def get_code(self):
        return '\n'.join(self.setup + self.lines + self.data)
    def add_command(self, comm, arg1 = "", arg2 = ""):
        self.lines.append("\t"+ comm +
                          ((" " + arg1) if arg1 else "") +
                          ((", " + arg2) if arg2 else ""))
    def get_label(self):
        label_name = "__label" + str(self.labelnum)
        self.labelnum += 1
        return label_name
        
    def add_label(self, label_name):
        self.lines.append(label_name + ":")

class Type:
    def __init__(self, type_name = "int", pointers = 0):
        self.type_name = type_name
        self.pointers = pointers
    def __repr__(self):
        return "*"*self.pointers + self.type_name
    def __eq__(self, other):
        return (self.type_name == other.type_name) and (self.pointers == other.pointers)

class StateInfo:
    def __init__(self, var_offset = 0, symbols = [], t = None):
        self.var_offset = var_offset # amount of offset from rbp for last variable, divided by 8
        self.symbols = symbols[:] # symbol table
        self.t = t
    def is_declared(self, name):
        return (name in [dec[0] for dec in self.symbols])
    def add(self, name, t):
        if self.is_declared(name): raise VariableRedeclarationException(name)
        else:
            s = self.c()
            s.var_offset += 1
            s.symbols += [(name, s.var_offset, t)]
            return s
    def get(self, name):
        var_loc = [var for var in self.symbols if var[0] == name]
        if var_loc:
            return (var_loc[0][1], var_loc[0][2])
        else:
            raise VariableNotDeclaredException(name)
    def c(self):
        return StateInfo(self.var_offset, self.symbols, self.t)


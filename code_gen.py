import rules
import tokens

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
        self.data = ["","\tsection .data", "var:\tdb 0"]
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

class StateInfo:
    def __init__(self, var_offset = 0, symbols = []):
        self.var_offset = var_offset # amount of offset from rbp for last variable, divided by 8
        self.symbols = symbols[:] # symbol table
    def c(self):
        return StateInfo(self.var_offset, self.symbols)

def make_code(root, info, code):
    if root.rule == rules.main_setup_form:
        info = make_code(root.children[4], info, code)
        
    elif root.rule == rules.statements_cont:
        info = make_code(root.children[0], info, code)
        code.add_command("mov", "rsp", "rbp")
        code.add_command("sub", "rsp", str(info.var_offset * 8)) # remove all temporary stack stuff
        info = make_code(root.children[1], info, code)
        
    elif root.rule == rules.statements_end:
        info = make_code(root.children[0], info, code)
        
    elif root.rule == rules.return_form:
        info = make_code(root.children[1], info, code)
        code.add_command("mov", "rax", "0x2000001")
        code.add_command("pop", "rdi")
        code.add_command("syscall")
        
    elif root.rule == rules.useless_declaration: pass
    
    elif root.rule == rules.real_declaration:
        # This one is unique because we have to parse the whole tree to get what we need
        node = root
        while node.rule != rules.base_declare: # get the type of this declaration
            node = node.children[0]
        dec_type = node.children[0].text
        if dec_type != "int": raise RuleGenException(root.rule) # only int supported right now
        
        else:
            node = root
            next_val = None
            declarations = []

            # Construct an ordered list of the declarations needed
            while node.rule != rules.base_declare:
                if node.rule == rules.real_declaration:
                    node = node.children[0]
                elif node.rule == rules.assign_declare:
                    next_val = node.children[2]
                    node = node.children[0]
                elif node.rule == rules.cont_declare:
                    declarations.append((node.children[2].text, next_val))
                    next_val = None
                    node = node.children[0]
            declarations.append((node.children[1].text, next_val))
            declarations.reverse()

            for (name, node) in declarations: 
                if name in [dec[0] for dec in info.symbols]: raise VariableRedeclarationException(name)
                
                if node:
                    info = make_code(node, info, code) # push the assigned value onto the stack
                else:
                    code.add_command("push", "0") # if no assignment, just push a random 0
                    
                info = info.c()
                info.var_offset += 1
                info.symbols += [(name, info.var_offset)]
                code.add_command("mov", "rsp", "rbp")
                code.add_command("sub", "rsp", str(info.var_offset * 8)) # remove all temporary stack stuff

    elif root.rule == rules.E_num:
        code.add_command("push", root.children[0].text)
        
    elif root.rule == rules.E_parens:
        info = make_code(root.children[1], info, code)
        
    elif root.rule == rules.E_add:
        info = make_code(root.children[0], info, code)
        info = make_code(root.children[2], info, code)
        code.add_command("pop", "rbx")
        code.add_command("pop", "rax")
        if root.children[1].text == "+": code.add_command("add", "rax", "rbx")
        elif root.children[1].text == "-": code.add_command("sub", "rax", "rbx")
        else: raise RuleGenException(root.rule)
        code.add_command("push","rax")
        
    elif root.rule == rules.E_mult:
        info = make_code(root.children[0], info, code)
        info = make_code(root.children[2], info, code)
        code.add_command("pop", "rbx")
        code.add_command("pop", "rax")
        code.add_command("imul", "rax", "rbx")
        code.add_command("push", "rax")
        
    elif root.rule == rules.E_div:
        info = make_code(root.children[0], info, code)
        info = make_code(root.children[2], info, code)
        code.add_command("pop", "rbx")
        code.add_command("pop", "rax")
        code.add_command("cqo")
        code.add_command("idiv", "rbx")
        code.add_command("push", "rax")
        
    elif root.rule == rules.E_mod:
        info = make_code(root.children[0], info, code)
        info = make_code(root.children[2], info, code)
        code.add_command("pop", "rbx")
        code.add_command("pop", "rax")
        code.add_command("mov", "rdx", "0")
        code.add_command("cqo")
        code.add_command("idiv", "rbx")
        code.add_command("push", "rdx")
        
    elif root.rule == rules.E_eq_compare:
        info = make_code(root.children[0], info, code)
        info = make_code(root.children[2], info, code)
        code.add_command("pop", "rbx")
        code.add_command("pop", "rax")
        code.add_command("mov", "rcx", "0")
        code.add_command("cmp", "rax", "rbx")
        if root.children[1].text == "==": code.add_command("sete", "cl")
        elif root.children[1].text == "!=": code.add_command("setne", "cl")
        else: raise RuleGenException(root.rule)
        code.add_command("push", "rcx")

    elif root.rule == rules.E_compare:
        info = make_code(root.children[0], info, code)
        info = make_code(root.children[2], info, code)
        code.add_command("pop", "rbx")
        code.add_command("pop", "rax")
        code.add_command("mov", "rcx", "0")
        code.add_command("cmp", "rax", "rbx")
        if root.children[1].text == "<": code.add_command("setl", "cl")
        elif root.children[1].text == "<=": code.add_command("setle","cl")
        elif root.children[1].text == ">": code.add_command("setg", "cl")
        elif root.children[1].text == ">=": code.add_command("setge", "cl")
        else: raise RuleGenException(root.rule)
        code.add_command("push", "rcx")
        
    elif root.rule == rules.E_neg:
        info = make_code(root.children[1], info, code)
        if root.children[0].text == "-":
            code.add_command("pop", "rax")
            code.add_command("neg", "rax")
            code.add_command("push", "rax")
            
    elif root.rule == rules.E_equal:
        var_loc = [var[1] for var in info.symbols if var[0] == root.children[0].text]
        if var_loc:
            # This could probably be shortened, but to be safe I want to do var_loc[0] asap
            # (in case make_code modifies the variable locations or something)
            code.add_command("mov", "rax", "[rbp - " + str(8*var_loc[0]) + "]")
            code.add_command("push", "rax")
            info = make_code(root.children[2], info, code)
            code.add_command("pop", "rbx")
            code.add_command("pop", "rax")
            
            if root.children[1] == tokens.equal:
                code.add_command("mov", "rax", "rbx")
            elif root.children[1] == tokens.plusequal:
                code.add_command("add", "rax", "rbx")
            elif root.children[1] == tokens.minusequal:
                code.add_command("sub", "rax", "rbx")
            elif root.children[1] == tokens.timesequal:
                code.add_command("imul", "rax", "rbx")
            elif root.children[1] == tokens.divequal:
                code.add_command("cqo")
                code.add_command("idiv", "rbx")
            elif root.children[1] == tokens.modequal:
                code.add_command("mov", "rdx", "0")
                code.add_command("idiv", "rbx")
                code.add_command("mov", "rax", "rdx")
            else: raise RuleGenException(root.rule)
            
            code.add_command("mov", "[rbp - " + str(8*var_loc[0]) + "]", "rax")
            code.add_command("push", "rax")
        else:
            raise VariableNotDeclaredException(root.children[0].text)

    elif root.rule == rules.E_inc_after:
        var_loc = [var[1] for var in info.symbols if var[0] == root.children[0].text]
        if var_loc:
            code.add_command("mov", "rax", "[rbp - " + str(8*var_loc[0]) + "]")
            code.add_command("push", "rax")
            if root.children[1].text == "++":
                code.add_command("inc", "rax")
            elif root.children[1].text == "--":
                code.add_command("dec", "rax")
            else: raise RuleGenException(root.rule)
            code.add_command("mov", "[rbp - " + str(8*var_loc[0]) + "]", "rax")
        else:
            raise VariableNotDeclaredException(root.children[0].text)
        
    elif root.rule == rules.E_inc_before:
        var_loc = [var[1] for var in info.symbols if var[0] == root.children[1].text]
        if var_loc:
            code.add_command("mov", "rax", "[rbp - " + str(8*var_loc[0]) + "]")
            if root.children[0].text == "++":
                code.add_command("inc", "rax")
            elif root.children[0].text == "--":
                code.add_command("dec", "rax")
            else: raise RuleGenException(root.rule)
            code.add_command("push", "rax")
            code.add_command("mov", "[rbp - " + str(8*var_loc[0]) + "]", "rax")
        else:
            raise VariableNotDeclaredException(root.children[1].text)

    elif root.rule == rules.E_var:
        var_loc = [var[1] for var in info.symbols if var[0] == root.children[0].text]
        if var_loc:
            code.add_command("mov", "rax", "[rbp - " + str(8*var_loc[0]) + "]")
            code.add_command("push", "rax")
        else:
            raise VariableNotDeclaredException(root.children[0].text)

    elif root.rule == rules.E_form:
        info = make_code(root.children[0], info, code)

    elif root.rule == rules.if_form_empty:
        info = make_code(root.children[1], info, code)

    elif root.rule == rules.if_form_oneline:
        info = make_code(root.children[1], info, code)
        code.add_command("pop", "rax")
        code.add_command("cmp", "rax", "0")
        endif_label = code.get_label()
        code.add_command("je", endif_label)
        info = make_code(root.children[3], info, code)
        code.add_label(endif_label)

    elif root.rule == rules.if_form_main:
        info = make_code(root.children[1], info, code)
        code.add_command("pop", "rax")
        code.add_command("cmp", "rax", "0")
        endif_label = code.get_label()
        code.add_command("je", endif_label)
        info_temp = make_code(root.children[4], info, code)
        code.add_label(endif_label)

    else:
        raise RuleGenException(root.rule)
    
    return info


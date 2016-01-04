import rules
import tokens
from lexer import *

from code_gen_obj import *

def make_code(root, info, code,
              has_else = False, endelse_label = ""): # adds an extra jump label if the "if" has an "else"
    
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
        while node.rule != rules.declare_type_base: # get the type of this declaration
            node = node.children[0]
        dec_type = node.children[0].text
        if dec_type != "int": raise RuleGenException(root.rule) # only int supported right now
        else:
            node = root
            next_val = None
            declarations = []

            def count_asterisks(node): # counts the number of asterisks on a DS node
                if len(node.children) == 1: return 0
                else: return 1 + count_asterisks(node.children[0])

            # Construct an ordered list of the declarations needed
            while True:
                if node.rule == rules.real_declaration:
                    node = node.children[0]
                elif node.rule == rules.assign_declare:
                    next_val = node.children[2]
                    node = node.children[0]
                elif node.rule == rules.cont_declare:
                    declarations.append((node.children[2].text, next_val, count_asterisks(node.children[1])))
                    next_val = None
                    node = node.children[0]
                elif node.rule == rules.base_declare:
                    declarations.append((node.children[1].text, next_val, count_asterisks(node.children[0])))
                    break

            declarations.reverse()

            for (name, node, pointers) in declarations: 
                if node:
                    info = make_code(node, info, code) # push the assigned value onto the stack
                else:
                    code.add_command("push", "0") # if no assignment, just push a random 0
                info = info.add(name, Type("int", pointers)) # this new variable will be created where the last thingy was pushed
                code.add_command("mov", "rsp", "rbp")
                code.add_command("sub", "rsp", str(info.var_offset * 8)) # remove all temporary stack stuff

    elif root.rule == rules.E_num:
        code.add_command("push", root.children[0].text)
        info.t = Type()
        
    elif root.rule == rules.E_parens:
        info = make_code(root.children[1], info, code)
        
    elif root.rule == rules.E_add:
        info = make_code(root.children[0], info, code)
        type1 = info.t
        info = make_code(root.children[2], info, code)
        type2 = info.t
        code.add_command("pop", "rbx")
        code.add_command("pop", "rax")

        if root.children[1].text == "+":
            # typecheck
            if type1.pointers == 0 and type2.pointers > 0:
                code.add_command("imul", "rax", 8)
            elif type2.pointers == 0 and type1.pointers > 0:
                code.add_command("imul", "rbx", 8)
            elif type1.pointers == 0 and type2.pointers == 0:
                pass
            else: raise RuleGenException(root.rule)
            code.add_command("add", "rax", "rbx")
        elif root.children[1].text == "-":
            if type1.pointers == 0 and type2.pointers == 0:
                code.add_command("sub", "rax", "rbx")
            elif type1.pointers > 0 and type2.pointers == 0:
                code.add_command("imul", "rbx", "8")
                code.add_command("sub", "rax", "rbx")
            elif type1.pointers > 0 and type2.pointers > 0 and type1.pointers == type2.pointers:
                code.add_command("sub", "rax", "rbx")
                code.add_command("cqo")
                code.add_command("idiv", "8")
            else: raise RuleGenException(root.rule)
        else: raise RuleGenException(root.rule)
        
        code.add_command("push","rax")
        info.t = Type("int", max(type1.pointers, type2.pointers))
        
    elif root.rule == rules.E_mult:
        info = make_code(root.children[0], info, code)
        type1 = info.t
        info = make_code(root.children[2], info, code)
        type2 = info.t
        if type1.pointers > 0 or type2.pointers > 0: raise RuleGenException(root.rule)
        
        code.add_command("pop", "rbx")
        code.add_command("pop", "rax")
        code.add_command("imul", "rax", "rbx")
        code.add_command("push", "rax")
        
    elif root.rule == rules.E_div:
        info = make_code(root.children[0], info, code)
        type1 = info.t
        info = make_code(root.children[2], info, code)
        type2 = info.t
        if type1.pointers > 0 or type2.pointers > 0: raise RuleGenException(root.rule)

        code.add_command("pop", "rbx")
        code.add_command("pop", "rax")
        code.add_command("cqo")
        code.add_command("idiv", "rbx")
        code.add_command("push", "rax")
        
    elif root.rule == rules.E_mod:
        info = make_code(root.children[0], info, code)
        type1 = info.t
        info = make_code(root.children[2], info, code)
        type2 = info.t
        if type1.pointers > 0 or type2.pointers > 0: raise RuleGenException(root.rule)

        code.add_command("pop", "rbx")
        code.add_command("pop", "rax")
        code.add_command("mov", "rdx", "0")
        code.add_command("cqo")
        code.add_command("idiv", "rbx")
        code.add_command("push", "rdx")

    elif root.rule == rules.E_boolean_and:
        info = make_code(root.children[0], info, code)
        code.add_command("pop", "rax")
        push_0 = code.get_label()
        end = code.get_label()
        code.add_command("cmp", "rax", "0")
        code.add_command("je", push_0)
        info = make_code(root.children[2], info, code)
        code.add_command("pop", "rax")
        code.add_command("cmp", "rax", "0")
        code.add_command("je", push_0)
        code.add_command("push", "1")
        code.add_command("jmp", end)
        code.add_label(push_0)
        code.add_command("push", "0")
        code.add_label(end)

        info.t = Type("int")

    elif root.rule == rules.E_boolean_or:
        info = make_code(root.children[0], info, code)
        code.add_command("pop", "rax")
        push_1 = code.get_label()
        end = code.get_label()
        code.add_command("cmp", "rax", "0")
        code.add_command("jne", push_1)
        info = make_code(root.children[2], info, code)
        code.add_command("pop", "rax")
        code.add_command("cmp", "rax", "0")
        code.add_command("jne", push_1)
        code.add_command("push", "0")
        code.add_command("jmp", end)
        code.add_label(push_1)
        code.add_command("push", "1")
        code.add_label(end)

        info.t = Type("int")
        
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

        info.t = Type("int")

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

        info.t = Type("int")
        
    elif root.rule == rules.E_neg:
        info = make_code(root.children[1], info, code)
        if info.t.pointers > 0: raise RuleGenException(root.rule)
        if root.children[0].text == "-":
            code.add_command("pop", "rax")
            code.add_command("neg", "rax")
            code.add_command("push", "rax")
            
    elif root.rule == rules.E_equal:
        if root.children[0].rule != rules.E_var: raise RuleGenException(root.rule)
        
        var_loc = info.get(root.children[0].children[0].text)
        # This could probably be shortened, but to be safe I want to var_loc asap
        # (in case make_code modifies the variable locations or something)
        code.add_command("mov", "rax", "[rbp - " + str(8*var_loc[0]) + "]")
        code.add_command("push", "rax")
        info = make_code(root.children[2], info, code)
        code.add_command("pop", "rbx")
        code.add_command("pop", "rax")
        ltype = var_loc[1]
        rtype = info.t

        if root.children[1] == tokens.equal:
            code.add_command("mov", "rax", "rbx")
            
        elif root.children[1] == tokens.plusequal:
            if ltype.pointers > 0 and rtype.pointers > 0: raise RuleGenException(root.rule)
            elif ltype.pointers > 0 and rtype.pointers == 0:
                code.add_command("imul", "rbx", "8")
            elif ltype.pointers == 0 and rtype.pointers > 0:
                code.add_command("imul", "rax", "8")
            code.add_command("add", "rax", "rbx")
        elif root.children[1] == tokens.minusequal:
            if ltype.pointers == 0 and rtype.pointers == 0:
                code.add_command("sub", "rax", "rbx")
            elif ltype.pointers > 0 and rtype.pointers == 0:
                code.add_command("imul", "rbx", "8")
                code.add_command("sub", "rax", "rbx")
            elif ltype.pointers > 0 and rtype.pointers > 0 and ltype.pointers == rtype.pointers:
                code.add_command("sub", "rax", "rbx")
                code.add_command("cqo")
                code.add_command("idiv", "8")
            else:
                raise RuleGenException(root.rule)
        elif root.children[1] == tokens.timesequal:
            if ltype.pointers > 0 or rtype.pointers > 0: raise RuleGenException(root.rule)
            code.add_command("imul", "rax", "rbx")
        elif root.children[1] == tokens.divequal:
            if ltype.pointers > 0 or rtype.pointers > 0: raise RuleGenException(root.rule)
            code.add_command("cqo")
            code.add_command("idiv", "rbx")
        elif root.children[1] == tokens.modequal:
            if ltype.pointers > 0 or rtype.pointers > 0: raise RuleGenException(root.rule)
            code.add_command("mov", "rdx", "0")
            code.add_command("idiv", "rbx")
            code.add_command("mov", "rax", "rdx")
        else: raise RuleGenException(root.rule)

        code.add_command("mov", "[rbp - " + str(8*var_loc[0]) + "]", "rax")
        code.add_command("push", "rax")

        info.t = ltype

    elif root.rule == rules.E_boolean_not:
        info = make_code(root.children[1], info, code)
        code.add_command("pop", "rax")
        code.add_command("cmp", "rax", "0")
        label_1 = code.get_label()
        label_2 = code.get_label()
        code.add_command("je", label_1)
        code.add_command("push", "0")
        code.add_command("jmp", label_2)
        code.add_label(label_1)
        code.add_command("push", "1")
        code.add_label(label_2)

    elif root.rule == rules.E_inc_after:
        if root.children[0].rule != rules.E_var: raise RuleGenException(root.rule)
        var_loc = info.get(root.children[0].children[0].text)
        code.add_command("mov", "rax", "[rbp - " + str(8*var_loc[0]) + "]")
        code.add_command("push", "rax")
        if root.children[1].text == "++":
            if var_loc[1].pointers == 0:
                code.add_command("inc", "rax")
            else:
                code.add_command("add", "rax", "8")
        elif root.children[1].text == "--":
            if var_loc[1].pointers == 0:
                code.add_command("dec", "rax")
            else:
                code.add_command("sub", "rax", "8")
        else: raise RuleGenException(root.rule)
        code.add_command("mov", "[rbp - " + str(8*var_loc[0]) + "]", "rax")
        info.t = var_loc[1]
        
    elif root.rule == rules.E_inc_before:
        if root.children[1].rule != rules.E_var: raise RuleGenException(root.rule)
        var_loc = info.get(root.children[1].children[0].text)
        code.add_command("mov", "rax", "[rbp - " + str(8*var_loc[0]) + "]")
        if root.children[0].text == "++":
            if var_loc[1].pointers == 0:
                code.add_command("inc", "rax")
            else:
                code.add_command("add", "rax", "8")
        elif root.children[0].text == "--":
            if var_loc[1].pointers == 0:
                code.add_command("dec", "rax")
            else:
                code.add_command("sub", "rax", "8")
        else: raise RuleGenException(root.rule)

        code.add_command("push", "rax")
        code.add_command("mov", "[rbp - " + str(8*var_loc[0]) + "]", "rax")
        info.t = var_loc[1]

    elif root.rule == rules.E_var:
        var_loc = info.get(root.children[0].text)
        code.add_command("mov", "rax", "[rbp - " + str(8*var_loc[0]) + "]")
        code.add_command("push", "rax")
        info.t = var_loc[1]

    elif root.rule == rules.E_form:
        info = make_code(root.children[0], info, code)

    elif root.rule in [rules.if_form_empty,
                       rules.if_form_brackets,
                       rules.if_form_oneline,
                       rules.if_form_main]:
        info = make_code(root.children[1], info, code)
        code.add_command("pop", "rax")
        code.add_command("cmp", "rax", "0")
        endif_label = code.get_label()
        code.add_command("je", endif_label)

        if root.rule == rules.if_form_main:
            make_code(root.children[4], info, code) # do not update info!
        elif root.rule == rules.if_form_oneline:
            make_code(root.children[3], info, code) # do not update info!
            
        if has_else:
            code.add_command("jmp", endelse_label)
        code.add_label(endif_label)

    elif root.rule in [rules.else_form_empty,
                       rules.else_form_brackets,
                       rules.else_form_oneline,
                       rules.else_form_main]:

        if root.rule == rules.else_form_oneline:
            make_code(root.children[1], info, code) # do not update info
        elif root.rule == rules.else_form_main:
            make_code(root.children[2], info, code) # do not update info

    elif root.rule == rules.if_form_general:
        info = make_code(root.children[0], info, code)

    elif root.rule == rules.ifelse_form_general:
        end_else = code.get_label()
        info = make_code(root.children[0], info, code, True, end_else)
        info = make_code(root.children[1], info, code)
        code.add_label(end_else)

    else:
        raise RuleGenException(root.rule)
    
    return info

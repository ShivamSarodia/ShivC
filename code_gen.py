import rules
import tokens
from lexer import *

from code_gen_obj import *

def make_code(root, info, code,
              has_else = False, endelse_label = "",  # adds an extra jump label if the "if" has an "else"
              loop_break = None, loop_continue = None):
    
    if root.rule == rules.main_setup_form:
        info = make_code(root.children[4], info, code)
        
    elif root.rule == rules.statements_cont:
        info = make_code(root.children[0], info, code, loop_break=loop_break, loop_continue=loop_continue)
        code.add_command("lea", "rsp", "[rbp - " + str(info.var_offset * 8) + "]") # remove all temporary stack stuff
        info = make_code(root.children[1], info, code, loop_break=loop_break, loop_continue=loop_continue)
        
    elif root.rule == rules.statements_end:
        info = make_code(root.children[0], info, code, loop_break=loop_break, loop_continue=loop_continue)
        
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
            next_array = False
            next_size = 0
            
            declarations = []

            def count_asterisks(node): # counts the number of asterisks on a DS node
                if len(node.children) == 1: return 0
                else: return 1 + count_asterisks(node.children[0])

            # Construct an ordered list of the declarations needed
            while True:
                if node.rule == rules.real_declaration:
                    node = node.children[0]
                elif node.rule == rules.assign_declare or node.rule == rules.arr_assign_declare:
                    next_val = node.children[2]
                    node = node.children[0]
                elif node.rule == rules.cont_declare:
                    declarations.append((node.children[2].text, next_val, count_asterisks(node.children[1]),
                                         next_array, next_size))
                    next_val = None
                    next_array = False
                    next_size = 0
                    node = node.children[0]
                elif node.rule == rules.array_num_declare:
                    if ((node.children[0].rule != rules.base_declare and node.children[0].rule != rules.cont_declare) or
                        node.children[2].rule != rules.E_num):
                        raise RuleGenException(node.rule)
                    next_array = True
                    next_size = int(node.children[2].children[0].text)
                    if next_size < 0: raise RuleGenException(node.rule)
                    node = node.children[0]
                elif node.rule == rules.array_nonum_declare:
                    if node.children[0].rule != rules.base_declare and node.children[0].rule != rules.cont_declare:
                        raise RuleGenException(node.rule)
                    next_array = True
                    next_size = None
                    node = node.children[0]
                elif node.rule == rules.base_declare:
                    declarations.append((node.children[1].text, next_val, count_asterisks(node.children[0]),
                                         next_array, next_size))
                    break

            declarations.reverse()

            def get_array(node): # coverts something like {1, 2, 3} to list, in reverse order
                if node.rule == rules.arr_list_none: return []
                elif node.rule == rules.arr_list_one: return [node.children[1]]
                elif node.rule == rules.arr_list_total:
                    return [node.children[1].children[0]] + get_array(node.children[0])
                elif node.rule == rules.arr_list_cont:
                    return [node.children[1]] + get_array(node.children[0])
                elif node.rule == rules.arr_list_start:
                    return [node.children[1]]
                else: raise RuleGenException(node.rule)

            for (name, node, pointers, is_array, array_len) in declarations:
                if not is_array:
                    if node:
                        info = make_code(node, info, code) # push the assigned value onto the stack
                    else:
                        code.add_command("push", "0") # if no assignment, just push a random 0
                    info = info.add(name, Type("int", pointers)) # this new variable will be created where the last thingy was pushed
                else:
                    if array_len is None and node is None: raise RuleGenException(root.rule)
                    
                    num_total = array_len
                    array_conts = get_array(node) if node else []

                    if num_total is not None:
                        if len(array_conts) > num_total: raise RuleGenException(root.rule)                    
                        # if the provided list is bigger than the provided size, complain

                        for i in range(num_total - len(array_conts)):
                            code.add_command("push", "0")
                            info = info.add_space()

                    for e in array_conts:
                        info = make_code(e, info, code) # push the node contents onto the stack
                        info = info.add_space()

                    code.add_command("lea", "rax", "[rbp - " + str(info.var_offset * 8) +  "]")
                    code.add_command("push", "rax")
                    info = info.add(name, Type("int", pointers + 1))
                
                code.add_command("lea", "rsp", "[rbp - " + str(info.var_offset * 8) +  "]")

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
                code.add_command("imul", "rax", "8")
            elif type2.pointers == 0 and type1.pointers > 0:
                code.add_command("imul", "rbx", "8")
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
                code.add_command("mov", "r8", "8")
                code.add_command("idiv", "r8")
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
            
    elif root.rule == rules.E_equal and root.children[1] == tokens.equal:
        left_base = root.children[0]
        while left_base.rule == rules.E_parens: left_base = left_base.children[1]
        
        if left_base.rule == rules.E_var:
            var_loc = info.get(left_base.children[0].text)
            info = make_code(root.children[2], info, code)
            code.add_command("pop", "rax")
            code.add_command("mov", "[rbp - " + str(8*var_loc[0]) + "]", "rax")
            code.add_command("push", "rax")
            info.t = var_loc[1]
        elif left_base.rule == rules.E_point:
            info = make_code(left_base.children[1], info, code)
            if info.t.pointers == 0: raise RuleGenException(root.rule)
            else: return_type = Type(info.t.type_name, info.t.pointers - 1)
            info = make_code(root.children[2], info, code)
            code.add_command("pop", "rbx")
            code.add_command("pop", "rax")
            code.add_command("mov", "[rax]", "rbx")
            code.add_command("push", "rbx")
            info.t = return_type
        elif left_base.rule == rules.E_array:
            info = make_code(left_base.children[2], info, code)
            info = make_code(left_base.children[0], info, code)
            info = make_code(root.children[2], info, code)
            info.t = Type(info.t.type_name, info.t.pointers - 1)
            code.add_command("pop", "rcx")
            code.add_command("pop", "rax")
            code.add_command("pop", "rbx")
            code.add_command("imul", "rbx", "8")
            code.add_command("add", "rax", "rbx")
            code.add_command("mov", "[rax]", "rcx")
            code.add_command("push", "rcx")

        else: raise RuleGenException(root.rule)
            
    elif root.rule == rules.E_equal: # not just simple equality
        left_base = root.children[0]
        while left_base.rule == rules.E_parens: left_base = left_base.children[1]
        
        if left_base.rule == rules.E_var: 
            var_loc = info.get(left_base.children[0].text)
            info = make_code(root.children[2], info, code)
            code.add_command("pop", "rbx")
            code.add_command("mov", "rax", "[rbp - " + str(8*var_loc[0]) + "]")
            ltype = var_loc[1]
            rtype = info.t
            save_loc = "[rbp - " + str(8*var_loc[0]) + "]"
        elif left_base.rule == rules.E_point:
            info = make_code(left_base.children[1], info, code)
            if info.t.pointers == 0: raise RuleGenException(root.rule)
            else: ltype = Type(info.t.type_name, info.t.pointers - 1)
            info = make_code(root.children[2], info, code)
            rtype = info.t
            code.add_command("pop", "rbx")
            code.add_command("pop", "rcx")
            code.add_command("mov", "rax", "[rcx]")
            save_loc = "[rcx]"
        elif left_base.rule == rules.E_array:
            info = make_code(left_base.children[2], info, code)
            info = make_code(left_base.children[0], info, code)
            if info.t.pointers == 0: raise RuleGenException(root.rule) 
            else: ltype = Type(info.t.type_name, info.t.pointers - 1)
            info = make_code(root.children[2], info, code)
            rtype = info.t
            code.add_command("pop", "rbx") # right hand side
            code.add_command("pop", "rcx") # rcx[r8]
            code.add_command("pop", "r8")
            code.add_command("imul", "r8", "8")
            code.add_command("add", "rcx", "r8")
            code.add_command("mov", "rax", "[rcx]")
            save_loc = "[rcx]"
        else: raise RuleGenException(root.rule)
            
        if root.children[1] == tokens.plusequal:
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
                code.add_command("mov", "r8", "8")
                code.add_command("idiv", "r8")
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

        code.add_command("mov", save_loc, "rax")
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
        left_base = root.children[0]
        while left_base.rule == rules.E_parens: left_base = left_base.children[1]

        if left_base.rule == rules.E_var:
            var_loc = info.get(left_base.children[0].text)
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
        elif left_base.rule == rules.E_point:
            info = make_code(left_base.children[1], info, code)
            code.add_command("pop", "rax")
            code.add_command("push", "qword [rax]")
            if info.t.pointers == 0: raise RuleGenException(root.rule)
            info.t = Type(info.t.type_name, info.t.pointers-1)
            if root.children[1].text == "++":
                if info.t.pointers == 0:
                    code.add_command("inc", "qword [rax]")
                else:
                    code.add_command("add", "qword [rax]", "8")
            elif root.children[1].text == "--":
                if info.t.pointers == 0:
                    code.add_command("dec", "qword [rax]")
                else:
                    code.add_command("sub", "qword [rax]", "8")
            else: raise RuleGenException(root.rule)
        elif left_base.rule == rules.E_array:
            info = make_code(left_base.children[2], info, code)
            info = make_code(left_base.children[0], info, code)
            if info.t.pointers == 0: raise RuleGenException(root.rule) 
            info.t = Type(info.t.type_name, info.t.pointers - 1)
            code.add_command("pop", "rax") # right hand side
            code.add_command("pop", "rbx") # rcx[r8]
            code.add_command("imul", "rbx", "8")
            code.add_command("add", "rax", "rbx")
            code.add_command("push", "qword [rax]")
            if root.children[1].text == "++":
                if info.t.pointers == 0:
                    code.add_command("inc", "qword [rax]")
                else:
                    code.add_command("add", "qword [rax]", "8")
            elif root.children[1].text == "--":
                if info.t.pointers == 0:
                    code.add_command("dec", "qword [rax]")
                else:
                    code.add_command("sub", "qword [rax]", "8")
            else: raise RuleGenException(root.rule)

            
    elif root.rule == rules.E_inc_before:
        left_base = root.children[1]
        while left_base.rule == rules.E_parens: left_base = left_base.children[1]

        if left_base.rule == rules.E_var:
            var_loc = info.get(left_base.children[0].text)
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
        elif left_base.rule == rules.E_point:
            info = make_code(left_base.children[1], info, code)
            code.add_command("pop", "rax")
            if info.t.pointers == 0: raise RuleGenException(root.rule)
            info.t = Type(info.t.type_name, info.t.pointers-1)
            if root.children[0].text == "++":
                if info.t.pointers == 0:
                    code.add_command("inc", "qword [rax]")
                else:
                    code.add_command("add", "qword [rax]", "8")
            elif root.children[0].text == "--":
                if info.t.pointers == 0:
                    code.add_command("dec", "qword [rax]")
                else:
                    code.add_command("sub", "qword [rax]", "8")
            else: raise RuleGenException(root.rule)
            code.add_command("push", "qword [rax]")
        elif left_base.rule == rules.E_array:
            info = make_code(left_base.children[2], info, code)
            info = make_code(left_base.children[0], info, code)
            if info.t.pointers == 0: raise RuleGenException(root.rule) 
            info.t = Type(info.t.type_name, info.t.pointers - 1)
            code.add_command("pop", "rax") # right hand side
            code.add_command("pop", "rbx") # rcx[r8]
            code.add_command("imul", "rbx", "8")
            code.add_command("add", "rax", "rbx")
            if root.children[0].text == "++":
                if info.t.pointers == 0:
                    code.add_command("inc", "qword [rax]")
                else:
                    code.add_command("add", "qword [rax]", "8")
            elif root.children[0].text == "--":
                if info.t.pointers == 0:
                    code.add_command("dec", "qword [rax]")
                else:
                    code.add_command("sub", "qword [rax]", "8")
            else: raise RuleGenException(root.rule)
            code.add_command("push", "qword [rax]")

    elif root.rule == rules.E_point:
        info = make_code(root.children[1], info, code)
        if info.t.pointers == 0: raise RuleGenException(root.rule)
        code.add_command("pop", "rax")
        code.add_command("push", "qword [rax]")
        info.t = Type(info.t.type_name, info.t.pointers - 1)

    elif root.rule == rules.E_deref:
        left_base = root.children[1]
        while left_base.rule == rules.E_parens: left_base = left_base.children[1]

        if left_base.rule == rules.E_var: 
            var_loc = info.get(left_base.children[0].text)
            code.add_command("lea", "rax", "[rbp - " + str(8*var_loc[0]) + "]")
            code.add_command("push", "rax")
            info.t = Type(var_loc[1].type_name, var_loc[1].pointers + 1)
        elif left_base.rule == rules.E_point:
            info = make_code(left_base.children[1], info, code)
            if info.t.pointers == 0: raise RuleGenException(root.rule)
        elif left_base.rule == rules.E_array:
            info = make_code(left_base.children[2], info, code)
            info = make_code(left_base.children[0], info, code)
            if info.t.pointers == 0: raise RuleGenException(root.rule)
            code.add_command("pop", "rax")
            code.add_command("pop", "rbx")
            code.add_command("imul", "rbx", "8")
            code.add_command("add", "rax", "rbx")
            code.add_command("push", "rax")
        else: raise RuleGenException(root.rule)

    elif root.rule == rules.E_array:
        info = make_code(root.children[2], info, code)
        info = make_code(root.children[0], info, code)
        info.t = Type(info.t.type_name, info.t.pointers - 1)
        code.add_command("pop", "rax")
        code.add_command("pop", "rbx")
        code.add_command("imul", "rbx", "8")
        code.add_command("add", "rax", "rbx")
        code.add_command("push", "qword [rax]")

    elif root.rule == rules.E_var:
        var_loc = info.get(root.children[0].text)
        code.add_command("push", "qword [rbp - " + str(8*var_loc[0]) + "]")
        info.t = var_loc[1]

    elif root.rule == rules.E_form:
        info = make_code(root.children[0], info, code)

    elif root.rule in [rules.if_form_empty,
                       rules.if_form_brackets,
                       rules.if_form_oneline,
                       rules.if_form_main]:
        info = make_code(root.children[1], info, code, loop_break=loop_break, loop_continue=loop_continue)
        code.add_command("pop", "rax")
        code.add_command("cmp", "rax", "0")
        endif_label = code.get_label()
        code.add_command("je", endif_label)

        if root.rule == rules.if_form_main:
            make_code(root.children[4], info, code, loop_break=loop_break, loop_continue=loop_continue) # do not update info
        elif root.rule == rules.if_form_oneline:
            make_code(root.children[3], info, code, loop_break=loop_break, loop_continue=loop_continue) # do not update info
            
        if has_else:
            code.add_command("jmp", endelse_label)
        code.add_label(endif_label)

    elif root.rule in [rules.else_form_empty,
                       rules.else_form_brackets,
                       rules.else_form_oneline,
                       rules.else_form_main]:

        if root.rule == rules.else_form_oneline:
            make_code(root.children[1], info, code, loop_break=loop_break, loop_continue=loop_continue) # do not update info
        elif root.rule == rules.else_form_main:
            make_code(root.children[2], info, code, loop_break=loop_break, loop_continue=loop_continue) # do not update info

    elif root.rule == rules.if_form_general:
        info = make_code(root.children[0], info, code, loop_break=loop_break, loop_continue=loop_continue)

    elif root.rule == rules.ifelse_form_general:
        end_else = code.get_label()
        info = make_code(root.children[0], info, code, True, end_else, loop_break=loop_break, loop_continue=loop_continue)
        info = make_code(root.children[1], info, code, loop_break=loop_break, loop_continue=loop_continue)
        code.add_label(end_else)

    elif root.rule == rules.break_form:
        if loop_break:
            code.add_command("jmp", loop_break)
        else:
            raise RuleGenException(root.rule)

    elif root.rule == rules.cont_form:
        if loop_continue:
            code.add_command("jmp", loop_continue)
        else:
            raise RuleGenException(root.rule)

    elif root.rule == rules.while_form_empty or root.rule == rules.while_form_brackets:
        info = make_code(root.children[1], info, code)

    elif root.rule == rules.while_form_main or root.rule == rules.while_form_oneline:
        startwhile = code.get_label()
        endwhile = code.get_label()
        
        code.add_label(startwhile)
        info = make_code(root.children[1], info, code)
        code.add_command("pop", "rax")
        code.add_command("cmp", "rax", "0")
        code.add_command("je", endwhile)
        if root.rule == rules.while_form_oneline:
            make_code(root.children[3], info, code, loop_break = endwhile, loop_continue = startwhile) # do not update info
        elif root.rule == rules.while_form_main:
            make_code(root.children[4], info, code, loop_break = endwhile, loop_continue = startwhile) # do not update info
        code.add_command("lea", "rsp", "[rbp - " + str(info.var_offset * 8) +  "]") # move rsp back to its place before going on
        code.add_command("jmp", startwhile)
        code.add_label(endwhile)
        
    else:
        raise RuleGenException(root.rule)
    
    return info

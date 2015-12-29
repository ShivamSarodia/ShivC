import rules

class CodeManager:
    def __init__(self):
        self.setup = ["\tglobal start", "", "\tsection .text", "", "start:"]
        self.lines = []
        self.data = ["","\tsection .data", "var:\tdb 0"]
    def get_code(self):
        return '\n'.join(self.setup + self.lines + self.data)
    def add_command(self, comm, arg1 = "", arg2 = ""):
        self.lines.append("\t"+ comm +
                          ((" " + arg1) if arg1 else "") +
                          ((", " + arg2) if arg2 else ""))

def make_code(root, info, code):
    if root.rule == rules.main:
        make_code(root.children[5], info, code)
    elif root.rule == rules.statements_cont:
        make_code(root.children[0], info, code)
        make_code(root.children[1], info, code)
    elif root.rule == rules.statements_end:
        make_code(root.children[0], info, code)
    elif root.rule == rules.return_form:
        make_code(root.children[1], info, code)
        code.add_command("mov", "rax", "0x2000001")
        code.add_command("pop", "rdi")
        code.add_command("syscall")
    elif root.rule == rules.math_num:
        code.add_command("push", root.children[0].text)
    elif root.rule == rules.math_parens:
        make_code(root.children[1], info, code)
    elif root.rule == rules.math_add:
        make_code(root.children[0], info, code)
        make_code(root.children[2], info, code)
        code.add_command("pop", "rbx")
        code.add_command("pop", "rax")
        if root.children[1].text == "+": code.add_command("add", "rax", "rbx")
        elif root.children[1].text == "-": code.add_command("sub", "rax", "rbx")
        code.add_command("push","rax")
    elif root.rule == rules.math_mult:
        make_code(root.children[0], info, code)
        make_code(root.children[2], info, code)
        code.add_command("pop", "rbx")
        code.add_command("pop", "rax")
        code.add_command("imul", "rax", "rbx")
        code.add_command("push", "rax")
    elif root.rule == rules.math_div:
        make_code(root.children[0], info, code)
        make_code(root.children[2], info, code)
        code.add_command("pop", "rbx")
        code.add_command("pop", "rax")
        code.add_command("cqo")
        code.add_command("idiv rbx")
        code.add_command("push", "rax")
    elif root.rule == rules.math_mod:
        make_code(root.children[0], info, code)
        make_code(root.children[2], info, code)
        code.add_command("pop", "rbx")
        code.add_command("pop", "rax")
        code.add_command("mov rdx, 0")
        code.add_command("cqo")
        code.add_command("idiv rbx")
        code.add_command("push", "rdx")
    elif root.rule == rules.math_neg:
        make_code(root.children[1], info, code)
        if root.children[0].text == "-":
            code.add_command("pop", "rax")
            code.add_command("neg", "rax")
            code.add_command("push", "rax")
    
    return code.get_code()


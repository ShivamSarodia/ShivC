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
        make_code(root.children[5], None, code)
    elif root.rule == rules.return_form:
        code.add_command("mov", "rax", "0x2000001")
        code.add_command("mov", "rdi", root.children[1].info)
        code.add_command("syscall")
    
    return code.get_code()


"""
Main file for ShivC. Compiles the provided C file into assembly, which is then
assembled by NASM and linked by ld into a final executable.
"""

import sys, subprocess, argparse

from lexer import *
import tokens

from parser import *
import rules

from code_gen import *

class NoMainFunctionException(Exception):
    def __str__(self): return "No \"int main()\" function found."

if __name__=="__main__":

    # Parse the command-line arguments
    parser = argparse.ArgumentParser(description='A small C compiler.')

    # The input .c file name
    parser.add_argument('input', metavar='input_file',
                        type=argparse.FileType('r'), help="the input c file")

    # The output file name
    parser.add_argument('-o', metavar='output_file', dest='output',
                        help="the name for the output files")

    # A flag to create only the asm file
    parser.add_argument('-S', dest='asm_only', action='store_const', const=True,
                        default=False, help="create only the assembly file")
    args = parser.parse_args()

    try:
        # Read the input file
        program_text = args.input.read()
    except:
        print("Could not read input file.")
    else:
        # If the file opened and was read, then carry on with tokenizing
        try:
            token_list = tokenize(program_text, tokens.prims)
        except TokenException as e: # catch any exceptions from the lexer
            print(e)
            sys.exit(1)
        else:
            try:
                # Parse the input into a syntax tree. See parser.py for
                # documentation on what all these parameters are.
                parse_root = generate_tree(token_list, rules.rules, rules.S,
                                           tokens.comment_start,
                                           tokens.comment_end,
                                           add_rule = rules.E_add,
                                           neg_rule = rules.E_neg,
                                           mult_rule = rules.E_mult,
                                           pointer_rule = rules.E_point,
                                           dec_sep_rule = rules.declare_separator_base,
                                           dec_exp_symbol = rules.declare_expression)
            except ParseException as e: # catch any exceptions from the parser
                print(e)
                sys.exit(1)
            else:
                try:
                    # As defined/explained in code_gen_obj.py
                    code = CodeManager()
                    info = StateInfo()

                    # Traverse the tree and generate asm into the CodeManager object
                    info = make_code(parse_root, info, code)

                    # Check if main function exists and has right type
                    mainfunc = info.get_func("main")
                    if mainfunc["args"] or mainfunc["ftype"] != Type("int", 0): raise NoMainFunctionException()

                    # Saves code string to complete_code
                    complete_code = code.get_code(mainfunc["label"])
                except (RuleGenException,
                        VariableRedeclarationException,
                        VariableNotDeclaredException,
                        NoMainFunctionException) as e:
                    # Catch any exceptions from the code generation step

                    print(e)
                    sys.exit(1)
                else:
                    try:
                        # Open the file for saving generated asm code
                        if args.output: output_name = args.output
                        else: output_name = args.input.name.split(".")[0]

                        g = open(output_name + ".s", "w")
                    except:
                        print("Could not create output asm file.")
                    else:
                        # Write the code to the file

                        g.write(complete_code)
                        g.close()

                        print("Compilation completed.")

                        # Compile the file into a final executable
                        # TODO: check version of nasm first
                        if not args.asm_only:
                            subprocess.call(["nasm", "-f", "macho64", output_name + ".s"])
                            subprocess.call(["ld", output_name + ".o", "-o", output_name])
                            print("Done.")
    finally:
        args.input.close()

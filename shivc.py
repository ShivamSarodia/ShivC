import sys

from lexer import *
from parser import *
import rules

usage = "Usage: shivc.py <input_c_file> [output_asm_file]"

if __name__=="__main__":
    
    # Get arguments and all that icky stuff
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print(usage)
        sys.exit()
    elif len(sys.argv) == 2:
        input_name = str(sys.argv[1])
        if len(input_name) > 2:
            output_name = input_name[:-2] + ".s" if input_name[-2:]==".c" else input_name + ".s"
        else:
            output_name = input_name + ".s"
    elif len(sys.argv) == 3:
        input_name = str(sys.argv[1])
        output_name = str(sys.argv[2])

    # Open the input file
    try:
        f = open(input_name, "r")
    except:
        print("Could not open input file. " + usage)
    else: # if the file opened, try reading it
        try:
            program = f.read()
        except:
            print("Could not read input file.")
        else: #if the file opened and was read, then carry on with tokenizing
            try:
                tokens = tokenize(program)
            except TokenException as e: # catch any exceptions from the lexer
                print(e)
            else:
                try:
                    parse_root = generate_tree(tokens, rules.rules, rules.S)
                except ParseException as e: # catch any exceptiosn from the parser
                    print(e)
                else:
                    print(parse_root)
        finally:
            f.close()

            

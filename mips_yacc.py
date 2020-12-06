import ply.yacc as yacc
import sys
from mips_lex import tokens
from optparse import OptionParser
from optimization import Dependency, DependencyGraph, Nope, Line, NOP, END

names = {
"$s0": 0,
"$s1": 0,
"$s2": 0,
"$s3": 0,
"$s4": 0,
"$s5": 0,
"$s6": 0,
"$s7": 0,
"$s8": 0,
"$s9": 0,
"$t0": 0,
"$t1": 0,
"$t2": 0,
"$t3": 0,
"$t4": 0,
"$t5": 0,
"$t6": 0,
"$t7": 0,
"$t8": 0,
"$t9": 0,
}


def p_statement_expr(t):
    'statement : expression'


def p_expression(t):
    '''expression : LINE_NUMBER ADD REGISTER REGISTER REGISTER
                | LINE_NUMBER SUB REGISTER REGISTER REGISTER
                | LINE_NUMBER OR REGISTER REGISTER REGISTER
                | LINE_NUMBER AND REGISTER REGISTER REGISTER
                | LINE_NUMBER ADDI REGISTER REGISTER NUMBER
                | LINE_NUMBER LW REGISTER NUMBER LPAREN REGISTER RPAREN
                | LINE_NUMBER SW REGISTER NUMBER LPAREN REGISTER RPAREN
                | LINE_NUMBER NOP
                | LINE_NUMBER END
                | LINE_NUMBER SHOW'''
    try:
        if t[2] == 'add': 
            names[t[3]] = names[t[4]] - names[t[5]] 
            lines.append(Line(t[1], t[2], t[3], [t[4], t[5]]))
        elif t[2] == 'sub': 
            names[t[3]] = names[t[4]] - names[t[5]]
            lines.append(Line(t[1], t[2], t[3], [t[4], t[5]]))
        elif t[2] == 'or': 
            names[t[3]] = names[t[4]] | names[t[5]]
            lines.append(Line(t[1], t[2], t[3], [t[4], t[5]]))
        elif t[2] == 'and': 
            names[t[3]] = names[t[4]] & names[t[5]]
            lines.append(Line(t[1], t[2], t[3], [t[4], t[5]]))
        elif t[2] == 'addi': 
            names[t[3]] = names[t[4]] + t[5]
            lines.append(Line(t[1], t[2], t[3], [t[4], str(t[5])]))
        elif t[2] == "lw": 
            names[t[3]] = 0
            lines.append(Line(t[1], t[2], t[3], [str(t[4]), '(', t[6], ')']))
        elif t[2] == "sw": 
            names[t[3]] = names[t[6]]
            lines.append(Line(t[1], t[2], None, [str(t[3]),str(t[4]), '(', t[6], ')']))
        elif t[2] == "nop": 
            lines.append(NOP(t[1]))
        elif t[2] == "end": 
            lines.append(END(t[1]))
        elif t[2] == "show": 
            pass
        else:
            print("There is some problem")
            for i in t:
                print(i)
        #parser.statements[t[1].lstrip()] = [char for char in t[2:] if char not in ["(", ")"]] 
    except KeyError as e:
        print(e)
        print(names)
        print("Run time error: Some registers in line '%d' have not been defined."% t.lexer.lineno)
        sys.exit(-1)

def p_error(t):
    print(names)
    print("Syntax error at '%s'" % t)


if __name__ == "__main__":
    parser = OptionParser() 
    parser.add_option("-f", "--forward", dest="forward")
    parser.add_option("-n", "--noforward", dest="noforward")
    parser.add_option("-s", "--schedule", dest="schedule")
    parser.add_option("-d", "--check_dependency", dest="checkup")
    parser.add_option("-p", "--path", dest="readfile" )

    (args, _) = parser.parse_args()
    print(args)
    parser = yacc.yacc()

    try:
        with open(args.readfile) as asm_file:
            code = asm_file.readlines()
    except KeyError as e:
        print(e)
        sys.exit(-1)

    lines = []
    end_exists =  False 
    try:
        for i in range(0, len(code)):
            if code[i].split()[1] == r'end':
                code = code[0:i+1]
                end_exists = True
                break
        if not end_exists:
            raise AssertionError
    except Exception:
        print("EOF (end) expected.")
        sys.exit(-1)
    for line in code: # run the code
        parser.parse("\n"+line)

    if args.noforward == "yes":
        DG = DependencyGraph(lines)
        noper = Nope()
        noper.add_nops(DG.dependencies, DG.lines, forwarding=False)
    elif args.forward == "yes":
        DG = DependencyGraph(lines)
        noper = Nope()
        noper.add_nops(DG.dependencies, DG.lines, forwarding=True)  
    elif args.schedule == "yes":
        DG = DependencyGraph(lines, out_of_order=True)
        DG.get_edges()
        DG.get_dependency_tree()
        DG.print_nop_loc()
        DG.print_dependency_graph()
        DG.scheduler()
    elif args.checkup == "yes":
        DG = DependencyGraph(lines, out_of_order=False)
        DG.print_dependencies()
    else: 
        raise FileNotFoundError
        


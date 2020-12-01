import ply.yacc as yacc
import sys
from mips_lex import tokens

names = {"$s0": 0,
"$s1": 0,
"$s2": 0,
"$s3": 0,
"$s4": 0,
"$s5": 0,
"$s6": 0,
"$s7": 0,
"$t0": 0,
"$t1": 0,
"$t2": 0,
"$t3": 0,
"$t4": 0,
"$t5": 0,
"$t6": 0,
"$t7": 0,}

class Parser(object):
    def __init__(self):
        self.statements = { }
        self.parser = None
        self.code = None
        self.eof = False
        self.program_counter = 0
        self.solver = None
    def initialize_parser(self):
        self.parser = yacc.yacc()
    def set_code(self, code):
        self.code = code
    def parse_code(self):
        for line in self.code:
            self.parser.parse("\n"+line)
    def parse_one_line(self):
        self.parser.parse("\n"+self.code[self.program_counter])
        self.program_counter += 1

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
            parser.solver.solver(w_reg=t[3], r_regs=[t[4], t[5]])
        elif t[2] == 'sub': 
            names[t[3]] = names[t[4]] - names[t[5]]
            parser.solver.solver(w_reg=t[3], r_regs=[t[4], t[5]])
        elif t[2] == 'or': 
            names[t[3]] = names[t[4]] | names[t[5]]
            parser.solver.solver(w_reg=t[3], r_regs=[t[4], t[5]])
        elif t[2] == 'and': 
            names[t[3]] = names[t[4]] & names[t[5]]
            parser.solver.solver(w_reg=t[3], r_regs=[t[4], t[5]])
        elif t[2] == 'addi': 
            names[t[3]] = names[t[4]] + t[5]
            parser.solver.solver(w_reg=t[3], r_regs=[t[4]])
        elif t[2] == "lw": 
            names[t[3]] = 0
            parser.solver.solver(w_reg=t[3], r_regs=[t[6]])
        elif t[2] == "sw": 
            names[t[3]] = names[t[6]]
            parser.solver.solver(w_reg=t[3], r_regs=[t[6]])
        elif t[2] == "nop": 
            pass
        elif t[2] == "end": 
            parser.eof = True
        elif t[2] == "show": 
            print(parser.statements)
        else:
            print("There is some problem")
            for i in t:
                print(i)
        parser.statements[t[1].lstrip()] = [char for char in t[2:] if char not in ["(", ")"]] 
    except KeyError as e:
        print(e)
        print(names)
        print("Run time error: Some registers in line '%d' have not been defined."% t.lexer.lineno)
        sys.exit(-1)
def p_error(t):
    print(names)
    print("Syntax error at '%s'" % t)


print("asm is activated, fetching input. . .\n\n")
parser = Parser()
parser.initialize_parser()
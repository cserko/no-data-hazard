import ply.yacc as yacc
from mips_lex import tokens
from mips_yacc import Parser, parser

class DataHazardSolver(object):
    def __init__(self):
        self.statements = []
        self.line_no = 1
        self.write_line = { }
        self.read_line = { }        

    def solver(self, write_reg, read_regs):
        if write_reg is not None or read_regs is not None:
            self.initialize_reg(write_reg, read_regs)
            self.write_line[self.line_no] = write_reg
            for read_reg in read_regs:
                self.read_line[read_reg].append(self.line_no)
            self.line_no += 1

    def initialize_reg(self, w_reg, read_regs):
        if self.line_no not in self.write_line.keys():
            self.write_line[self.line_no] = None
        for read_reg in read_regs:
            if read_reg not in self.read_line.keys(): self.read_line[read_reg] = []


class CompileTimeSolver(DataHazardSolver):
    def __init__(self):
        super(CompileTimeSolver, self).__init__()

    def solver(self, w_reg=None, r_regs=None):
        super(CompileTimeSolver, self).solver(w_reg, r_regs)


    def refactor(self):
        new_code = []
        line_nops = { }

        def get_dependent(read_list, write_line):
            if read_list is None: return None
            for i in read_list: 
                if i > write_line: return i
            # else returns None
        def total_nops(line, nops):
            count = 0
            for i in range(1, line):
                if i in nops.keys():
                    count += 1
            return count 

        for line in self.write_line.keys():
            write_reg = self.write_line[line]
            try:
                raw_loc = get_dependent(self.read_line[write_reg], line) # read after write dependency occuring at line
                if raw_loc is not None: # check if possible RAW and make sure no inner dependency
                    # there might be a raw hazard
                    print("at lines {}-{} on {} there might be a RAW hazard".format(line, raw_loc, write_reg)) # the first dep. is enough to resolve in our case.
                    if raw_loc - line < 3: 
                        print(raw_loc, line)
                        line_nops[line] = 3 - raw_loc + line        
            except KeyError:
                print("No RAW dependency on register {}".format(write_reg))    
            
        for i in line_nops.keys():
            self.statements.insert(i+total_nops(i, line_nops), ["nop\n" for nop in range(line_nops[i])])
        for i in self.statements:
            print(i)

if __name__ == "__main__":
    with open("./input.txt") as asm_file:
        parser.set_code(asm_file.readlines())

    solver = CompileTimeSolver()
    parser.solver = solver
    while not parser.eof:
        parser.parse_one_line()
    solver.statements = parser.code
    solver.refactor()

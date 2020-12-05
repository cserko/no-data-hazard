import ply.yacc as yacc
import sys
from mips_lex import tokens
from optparse import OptionParser

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

hazards = {"raw": "RAW", "war": "WAR", "waw": "WAW"}

class Line(object):
    def __init__(self, lineno, operation, write, reads):
        self.lineno = lineno
        self.operation = operation
        self.write = write # can be none i.e. sw
        self.reads = reads # list
        self.computable = True
        self.writeable = True if operation != "sw" else False
    
    def __str__(self):
        wrt = self.write
        if self.operation in ["lw", "sw"]:
            self.reads[-4] = ''.join(self.reads[-4:len(self.reads)])
            self.reads[-3:len(self.reads)] = ""
        reads = ', '.join(self.reads)
        if self.write == None:
            wrt = self.reads[0]
            reads = ', '.join(self.reads[1:])

        return str(self.lineno).lstrip() + " " + self.operation + " " + wrt + ", " + reads

class NOP(Line):
    def __init__(self, lineno):
        self.lineno = lineno
        self.computable = False
    def __str__(self):
        return "{} nop".format(self.lineno)
class END(Line):
    def __init__(self, lineno):
        self.lineno = lineno
        self.computable = False
    def __str__(self):
        return "{} end".format(self.lineno)

class Node(object):
    def __init__(self, line=None):
        self.lineno = line
        self.raw_children = []

class Dependency(object):

    def __init__(self, lineno1, lineno2, register, operation, hazard=hazards["raw"]):
        self.hazard_type = hazard
        self.operation = operation
        self.register = register
        self.caused = lineno1
        self.affected = lineno2
        self.diff = abs(lineno2 - lineno1) 
        self.child = [] # dependency chain
    def __str__(self):
        return ("hazard type: {} \n caused lineno: {} \n affected lineno: {} \n on register: {} \n"
        .format(self.hazard_type, self.caused, self.affected, self.register) )


class DependencyGraph(object):
    def __init__(self, lines, out_of_order=False):
        self.out_of_order = out_of_order
        self.graph = []
        self.nop_loc = []
        self.lines = lines
        self.linecount = len(lines)
        self.dependencies = []
        self.nodes = [Node(line=i) for i in range(self.linecount + 1)]
        self.link_dependencies()


    def link_dependencies(self):
        cur_line = 0
        for write_line in range(cur_line, self.linecount):
            write = self.lines[write_line]
            if not write.computable:
                continue
            for read_line in range(write_line + 1, self.linecount ): 
                read = self.lines[read_line]
                if read.computable and write.write in read.reads:
                    self.dependencies.append(Dependency(write_line+1, read_line+1, write.write, write.operation))
                
                if self.out_of_order:
                    if read.computable and write.write == read.write:
                        self.dependencies.append(Dependency(write_line+1, read_line+1, write.write, write.operation, hazard=hazards["waw"]))
                    if read.computable and read.write in write.reads:
                        self.dependencies.append(Dependency(read_line+1, write_line+1, read.write, read.operation, hazard=hazards["war"]))
            cur_line += 1
    
    def get_edges(self):
        for i in self.dependencies:
            if i.hazard_type == hazards["raw"]:
                self.nodes[int(i.caused)].raw_children.append(int(i.affected))
        return self.nodes

    def get_dependency_tree(self):
        visited = {int(i.lineno.lstrip().rstrip()):False for i in self.lines if type(i) is not NOP}
        for i in self.lines:
            if i.computable:
                line = int(i.lineno.lstrip().rstrip())
                if not visited[line] == True:  
                    self.graph.append(self._get_dependency_tree_impl(line, Node(), visited))

    def _get_dependency_tree_impl(self, line, node, visited):

        if node.lineno == None:
            node.lineno = line
        if self.nodes[line].raw_children == []:
            visited[line] = True
            return node
        for child in self.nodes[line].raw_children:
            child_node = Node()
            node.raw_children.append(child_node)
            self._get_dependency_tree_impl(child, child_node, visited)

        visited[line] = True
        return node

    def print_dependency_graph(self):
        for part in self.graph: 
            print("--------")
            self._print_dependency_graph(part)
        print("--------")
        
    def _print_dependency_graph(self, node):
        print(node.lineno)
        if node.raw_children == []:
            return
        for child in node.raw_children:
            self._print_dependency_graph(child)
            print("/")

    def get_line_op(self, line):
        print(self.lines[line-1].operation)
        return self.lines[line-1].operation

    def print_each(self):
        [print(i) for i in self.dependencies]
    def print_nop_loc(self):
        for i in self.lines:
            if isinstance(i, NOP): self.nop_loc.append(int(i.lineno))
        print(self.nop_loc)


class Nope(object):
    def __init__(self):
        self.nf_lookup = {"lw": 2, "add": 2, "addi": 2, "or": 2, "sw": 0}
        self.wf_lookup = {"lw": 1, "add": 0, "addi": 0, "or": 0, "sw": 0}
        self.nop_after = { }
        self.code = None
        self.filename = None
    def add_nops(self, dependencies, code, forwarding=False):
        self.filename = "forward.txt" if forwarding == True else "noforward.txt"
        lookup = self.nf_lookup if not forwarding else self.wf_lookup
        self.code = code
        for dependency in dependencies:
            if - dependency.caused + dependency.affected < lookup[dependency.operation] + 1:
                nop = lookup[dependency.operation] + 1 - dependency.affected + dependency.caused
                if not dependency.caused in self.nop_after.keys(): 
                    self.nop_after[dependency.caused] = nop
        self.generate_code()

    def generate_code(self):
        added_nop = 0
        for lineno in self.nop_after.keys():
            nop_count = self.nop_after[lineno]
            for l in range(lineno + added_nop, len(self.code)):
                self.code[l].lineno = str(int(self.code[l].lineno) + nop_count)
            for i in range(nop_count):
                self.code.insert(lineno + i + added_nop, NOP(lineno + i + 1 + added_nop)) 
            added_nop += nop_count
        with open(self.filename, "w") as f:
            f.writelines([i.__str__().lstrip()+"\n" for i in self.code])
            #f.write("{} end".format(len(self.code)+1))


if __name__ == "__main__":
    parser = OptionParser() 
    parser.add_option("-f", "--forward", dest="forward")
    parser.add_option("-n", "--noforward", dest="noforward")
    parser.add_option("-s", "--schedule", dest="schedule")
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
    else: 
        raise FileNotFoundError
        


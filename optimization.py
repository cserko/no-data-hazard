import copy

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

class NOP():
    def __init__(self, lineno):
        self.lineno = lineno
        self.computable = False
    def __str__(self):
        return "{} nop".format(self.lineno)
class END():
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
        self.forest = []
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
    def print_dependencies(self):
        print("Listing Dependencies. . . ")
        flag = False
        for i in self.dependencies:
            if abs(i.caused - i.affected) < 2:
                print(i)
                flag = True
        if not flag:
            print("--- There is no dependency ---")
    
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
                    self.forest.append(self._get_dependency_tree_impl(line, Node(), visited))

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
        for part in self.forest: 
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

    def scheduler(self):
        self.active = {i:[False for j in self.lines ] for i in self.nop_loc} # reach -> line - 1
        #print(self.active)
        for nop_line in self.active.keys():
            for graph in self.forest:
                highest_line = -1
                self._scheduler(nop_line, graph, highest_line)

        self.replace()

    def _scheduler(self, nop_line, graph, highest_line):

        if highest_line > nop_line:
            return 
        elif graph.lineno < nop_line: #go down
            if self._all_big(nop_line, graph.raw_children) and self.active[nop_line][graph.lineno - 1] is not None:
                self.active[nop_line][graph.lineno - 1] = True
        elif highest_line + 2 < nop_line and self.active[nop_line][graph.lineno - 1] is not None: #go up
                self.active[nop_line][graph.lineno - 1] = True
        else:
            self.active[nop_line][graph.lineno - 1] = None

        if graph.raw_children == []:
            return

        highest_line = graph.lineno
        for child in graph.raw_children:
            self._scheduler(nop_line, child, highest_line)


    def _all_big(self, nop_line, node_list): # helper
        for i in node_list:
            if i.lineno <= nop_line + 1:
                return False
        return True

    def replace(self):
        line_line = { } # lineno:lineno
        print(self.active)
        self.available_table = [True for i in self.lines]
        for i in self.active.keys():
            try:
                line_line[i] = [k+1 for k,j in enumerate(self.active[i]) if j is True and self.available_table[k+1]][0]
                self.available_table[line_line[i]] = False 
            except IndexError:
                pass
        self.scheduled_lines = []
        count = 1
        for line in self.lines:
            ln = int(line.lineno.lstrip().rstrip())
            if ln in line_line.keys():
                self.scheduled_lines.append(copy.deepcopy(self.lines[line_line[ln] - 1]))
                self.scheduled_lines[-1].lineno = count
            elif ln not in line_line.values():
                self.scheduled_lines.append(copy.deepcopy(line))
                self.scheduled_lines[-1].lineno = count
            else:
                continue
            count += 1
        
        
        with open("scheduled.txt", "w") as f:
            f.writelines([i.__str__().lstrip()+"\n" for i in self.scheduled_lines[0:-1]])
            f.write(self.scheduled_lines[-1].__str__())


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
            f.writelines([i.__str__().lstrip().rstrip()+"\n" for i in self.code[0:-1]])
            f.write(self.code[-1].__str__().lstrip().rstrip())
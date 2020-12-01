import time
import os

class Processor():
    def __init__(self):   
        # register table that checks whether it's being processed in an instruction. 
        self.clock_time = 0
        self.reg_available = {j: [True for i in range(10)] for j in ["s", "t"]}
        
        self.fetch = None
        self.decode = None
        self.execute = None
        self.memory = None
        self.writeback = None

    def write(self, register):
        pass
    def unlock_write(self, register):
        pass
    def clock(self):
        self.clock_time += 1


class Instruction():
    def __init__(self, clock):
        self.start_clock = clock
        self.end_clock = None
        self.writing = False
        self.write_reg = None


# Instruction is sent to the processor.
# processor fetchs necessary info for pipelining
# written registers
# boot the processor

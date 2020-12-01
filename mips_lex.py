import ply.lex as lex 
import os, sys

# List of token names.
tokens = (

    'REGISTER_OVERFLOW',
    'NUMBER',
    'LINE_NUMBER',
    'REGISTER',
    'LPAREN',
    'RPAREN',
    'COMMA',
    'END',
    'ADD',
    'SUB',
    'AND',
    'OR',
    'ADDI',
    'LW',
    'SW',
    'NOP',
    'SHOW',

)

# Regular expression rules for simple tokens
t_REGISTER = r'\$[s,t][0-9]'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_ADD = r'add'
t_SUB = r'sub'
t_AND = r'and'
t_OR = r'or'
t_ADDI = r'addi'
t_LW = r'lw'
t_SW = r'sw'
t_END = r'end'
t_NOP = r'nop'
t_SHOW = r'show'


# A regular expression rules with some action code
def t_REGISTER_OVERFLOW(t):
    r'\$[s,t][0-9][0-9]+'
    print("Terminal Error, register out of bounds '%s'" % t.value)
    t.lexer.skip(1)
    raise OverflowError

def t_LINE_NUMBER(t):
    r'\n\d+'     
    if t.lexer.lineno != int(t.value):
        print("line number '%d' does not match with the current line count '%d'" % (int(t.value), t.lexer.lineno))
        sys.exit(-1)
    t.lexer.lineno += 1
    return t

def t_NUMBER(t):
    r'-?[0-9]+'  
    t.value = int(t.value)    
    return t

def t_newline(t):
    r'\n+'

    #print("Exiting. . .")
#ignore whitespaces and tabs
t_ignore  = ' \t[,]'

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()
# -----------------------------------------------------------------------------
# Name:        pluto2
# Purpose:     Recursive Descent Parser Demo
#
# Author:  Rula Khayrallah, Derek Lopes
#
# -----------------------------------------------------------------------------
"""
Recursive descent parser to recognize & evaluate simple arithmetic expressions

Supports the following grammar:
    <command> ::= <bool_expr>
    <bool_expr> ::= <bool_term> {OR <bool_term>}
    <bool_term> ::= <not_factor> {AND <not_factor>}
    <not_factor> ::= {NOT} <bool_factor>
    <bool_factor> ::= BOOL | LPAREN <bool_expr> RPAREN | <comparison>
    <comparison> ::= <arith_expr> [COMP_OP <arith_expr>]
    <arith_expr> ::= <term> {ADD_OP <term>}
    <term> ::= <factor> {MULT_OP <factor>}
    <factor>::= LPAREN <arith_expr> RPAREN | FLOAT | INT
"""
import lex
from operator import add, sub, mul, truediv

from operator import lt, gt, eq, ne, le, ge


# List of token names - required
tokens = ('FLOAT', 'INT',
          'ADD_OP', 'MULT_OP',
          'LPAREN', 'RPAREN',
          'BOOL', 'AND', 'OR',
          'NOT', 'COMP_OP')

# global variables
token = None
lexer = None
parse_error = False

# Regular expression rules for simple tokens
# r indicates a raw string in Python - less backslashes
t_ADD_OP = r'\+|-'
t_MULT_OP = r'\*|/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_AND = r'and'
t_OR = r'or'
t_NOT = r'not'
t_COMP_OP = r'<=|>=|<|>|==|!='


# Regular expression rules with some action code
# The order matters
def t_BOOL(t):
    r'True|False'
    if t.value == 'True':
        t.value = True
    else:
        t.value = False
    return t

def t_FLOAT(t):
    r'\d*\.\d+|\d+\.\d*'
    t.value = float(t.value)  # string must be converted to float
    return t

def t_INT(t):
    r'\d+'
    t.value = int(t.value)  # string must be converted to int
    return t

# For the homework, you will add a function for boolean tokens

# A string containing ignored characters (spaces and tabs)
t_ignore = ' \t'


# Lexical error handling rule
def t_error(t):
    global parse_error
    parse_error = True
    print("ILLEGAL CHARACTER: {}".format(t.value[0]))
    t.lexer.skip(1)


# For homework 2, add the comparison operators to this dictionary
SUPPORTED_OPERATORS = {'+': add, '-': sub, '*': mul, '/': truediv,
                       '<': lt, '>': gt, '<=': le, '>=': ge,
                       '==': eq, '!=': ne}


def command():
    """
    <command> ::= <bool_expr>
    """
    result = bool_expr()
    if not parse_error:  # no parsing error
        if token:  # if there are more tokens
            error('END OF COMMAND OR OPERATOR')
        else:
            print(result)

def bool_expr():
    """
    <bool_expr> ::= <bool_term> {OR <bool_term>}
    """
    result = bool_term()
    while token and token.type == 'OR': # 0 or more OR
        match()
        if not parse_error:
            """ OLD CODE THAT DIDNT WORK IF TRUE WAS FIRST

                After about two hours of debugging, I found
                that this was the problem portion of my
                code. Turns out that python's partial
                evaluation of boolean expressions made it
                so that bool_term would not get called if
                result was True. This meant it would stop
                parsing if it encountered this which is bad

            result = result or bool_term()
            """
            result2 = bool_term()
            result = result or result2
    return result

def bool_term():
    """
    <bool_term> ::= <not_factor> {AND <not_factor>}
    """
    result = not_factor()
    while token and token.type == 'AND': # 0 or more AND
        match()
        if not parse_error:
            """ OLD CODE THAT DIDNT WORK IF FALSE WAS FIRST

                Same issue as above but reversed boolean
                values.

            result = result and not_factor()
            """
            result2 = not_factor()
            result = result and result2
    return result

def not_factor():
    """
    <not_factor> ::= {NOT} <bool_factor>
    """
    notCount = 0
    while token and token.type == 'NOT':
        notCount += 1
        match()
    result = bool_factor()
    if notCount % 2 is not 0:
        result = not result
    return result

def bool_factor():
    """
    <bool_factor> ::= BOOL | LPAREN <bool_expr> RPAREN | <comparison>
    """
    if token and token.type == 'BOOL':
        result = token.value
        match()
        return result
    elif token and token.type == 'LPAREN':
        match()
        result = bool_expr()
        if token and token.type == 'RPAREN':
            match()
            return result
        else:
            error(')')
    else:
        result = comparison()
    return result

def comparison():
    """
    <comparison> ::= <arith_expr> [COMP_OP <arith_expr>]
    """
    result = arith_expr()
    if token and token.type == 'COMP_OP': # one optional COMP_OP
        operation = SUPPORTED_OPERATORS[token.value]
        match()  # match the operator
        operand = arith_expr()  # evaluate the operand
        if not parse_error:
            result = operation(result, operand)
    return result

def arith_expr():
    """
    <arith_expr> ::= <term> { ADD_OP <term>}
    """
    result = term()
    while token and token.type == 'ADD_OP': # 0 or more ADD_OP
        operation = SUPPORTED_OPERATORS[token.value]
        match()  # match the operator
        operand = term()  # evaluate the operand
        if not parse_error:
            result = operation(result, operand)
    return result


def term():
    """
    <term> ::= <factor> {MULT_OP <factor>}
    """
    result = factor()
    while token and token.type == 'MULT_OP':
        operation = SUPPORTED_OPERATORS[token.value]
        match()  # match the operator
        operand = factor()  # evaluate the operand
        if not parse_error:
            result = operation(result, operand)
    return result


def factor():
    """
    <factor>::= LPAREN <arith_expr> RPAREN | FLOAT | INT
    """
    if token and token.type == 'LPAREN':
        match()
        result = arith_expr()
        if token and token.type == 'RPAREN':
            match()
            return result
        else:
            error(')')
    elif token and (token.type == 'FLOAT' or token.type == 'INT'):
        result = token.value
        match()
        return result
    else:
        error('NUMBER')


def match():
    """
    Get the next token
    """
    global token
    token = lexer.token()


def error(expected):
    """
    Print an error message when an unexpected token is encountered, sets
    a global parse_error variable.
    :param expected: (string) '(' or 'NUMBER' or or ')' or anything else...
    :return: None
    """
    global parse_error
    if not parse_error:
        parse_error = True
        print('Parser error')
        print("Expected:", expected)
        if token:
            print('Got: ', token.value)
            print('line', token.lineno, 'position', token.lexpos)


def main():
    global token
    global lexer
    global parse_error
    # Build the lexer
    lexer = lex.lex()
    # Prompt for a command
    more_input = True
    while more_input:
        input_command = input("Pluto 2.0>>>")
        if input_command == 'q':
            more_input = False
            print('Bye for now')
        elif input_command:
            parse_error = False
            # Send the command to the lexer
            lexer.input(input_command)
            token = lexer.token()  # Get the first token in a global variable
            command()


if __name__ == '__main__':
    main()

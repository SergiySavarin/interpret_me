#!/usr/bin/env python
''' Compile your string with your own parser ruls.
    You can run this file like
    $ ./interpretator.py <file_name_for_compilaton>
    or
    $ python
    >>> from interpretator import repl
    >>> repl()
    m_lang>
    and try to input your expressions.
'''

from __future__ import division

from sys import argv

import math
import operator

SYMBOL = str
LIST = list
NUMBER = (int, float)

def parse(program):
    '''Read a scheme expression from a string.'''
    return read_from_tokens(tokenize(program))

def tokenize(string):
    '''Convert a string into a list of tokens.'''
    return string.replace('(', ' ( ') \
                 .replace(')', ' ) ') \
                 .replace(',', ' , ') \
                 .split()

def read_from_tokens(tokens):
    '''Read expressions from tokens.'''
    if len(tokens) == 0:
        raise SyntaxError('Unexpected EOF while reading')
    token = tokens.pop(0)
    if '(' == token:
        lst = []
        while tokens[0] != ')':
            lst.append(read_from_tokens(tokens))
        tokens.pop(0)

        return lst
    elif ')' == token:
        raise SyntaxError('Unexpected )')
    else:
        return char_indent(token)

def char_indent(token):
    '''Numbers will be numbers, everything else will be symbols.'''
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return token

def standart_env():
    ''' An environment for eval function using with some
        standart procedures.
    '''
    env = Env()
    env.update(vars(math))
    env.update({
        '-':operator.sub,
        '/':operator.div, '=':operator.eq,
        '+':          lambda *x: sum(reversed(x)),
        '*':          lambda *x: reduce(operator.mul, x, 1),
        'append':     operator.add,
        'head':       lambda x: '(' + str(x[0]) + ')',
        'tail':       lambda x: '(' + ','.join(map(str, x[1:])) + ')',
        'lenght':     len,
        'list':       lambda *x: list(x),
        'list?':      lambda x: isinstance(x, list),
        'map':        map,
        'max':        max,
        'min':        min,
        'not':        operator.not_,
        'null?':      lambda x: x == [],
        'number?':    lambda x: isinstance(x, NUMBER),
        'symbol':     lambda x: isinstance(x, SYMBOL)
        })
    return env

class Env(dict):
    ''' An environment: a dict of {'var': val} pairs,
        with an outer Env.
    '''
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer
    def find(self, var):
        '''Find var in Env dict.'''
        if var in self:
            return self
        else:
            return self.outer.find(var)

global_env = standart_env()

def repl(promt='m_lang> '):
    '''Promt for reading eval input and output.'''
    while True:
        val = eval(parse(raw_input(promt)))
        if val is not None:
            print langstr(val)

def langstr(exp):
    '''Convert Python object back into a input string.'''
    if isinstance(exp, list):
        return exp
    else:
        return str(exp)

def dict_exp(x, env=global_env):
    '''Convert expressions with ',' - comma in dict.'''
    i = 0
    dct = {}
    while i < len(x):
        if len(x) > (i + 1) and x[i+1] != ',':
            dct[eval(x[i], env)] = eval(x[i+1], env)
            i += 3
        elif x[i] != x[-1] and x[i+1] == ',':
            dct[eval(x[i], env)] = None
            i += 2
        else:
            dct[eval(x[i], env)] = None
            i += 1
    return dct


def eval(x, env=global_env):
    '''Evaluate an expression in an environment.'''
    if isinstance(x, SYMBOL):
        return env.find(x)[x]
    elif not isinstance(x, LIST):
        return x
    elif ',' in x:
        return dict_exp(x)
    elif isinstance(x[0], NUMBER):
        # create list from nubers in 'x' and adding
        # results of evaluating outher list with operators
        return [eval(exp, env) for exp in x]
    elif x[0] == 'var':
        (_, var, exp) = x
        env[var] = eval(exp, env)
    else:
        proc = eval(x[0], env)
        args = [eval(exp, env) for exp in x[1:]]
        return proc(*args)

if __name__ == '__main__':
    if argv[1]:
        try:
            with open(argv[1], 'r') as f:
                for line in f:
                    if line == '\n':
                        continue
                    else:
                        line = line.rstrip()
                        print 'Line from executed file: ', line
                        try:
                            if eval(parse(line)) != None:
                                print 'Execution result:        ', \
                                                        eval(parse(line))
                        except SyntaxError as err:
                            print err
                f.close()
        except SystemError as err:
            print err

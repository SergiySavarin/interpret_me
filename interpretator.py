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

Symbol = str
List = list
Number = (int, float)

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
            # print read_from_tokens(tokens)
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
        'number?':    lambda x: isinstance(x, Number),
        'symbol':     lambda x: isinstance(x, Symbol)
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

def eval(x, env=global_env):
    '''Evaluate an expression in an environment.'''
    if isinstance(x, Symbol):
        return env.find(x)[x]
    elif not isinstance(x, List):
        return x
    elif ',' in x:
        out_of_range = lambda i, x: x[i + 1] \
                                if len(x) > (i + 1) and x[i + 1] != ',' \
                                else None
        return {x[i]:out_of_range(i, x) for i in range(0, len(x), 3)}
    elif isinstance(x[0], Number):
        # (_, exp) = x
        return [exp for exp in x if not isinstance(exp, List)] + \
               [eval(exp, env) for exp in x if isinstance(exp, List)]
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

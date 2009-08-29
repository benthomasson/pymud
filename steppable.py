#!/usr/bin/env python

from pymud.coroutine import coroutine, step


@coroutine
def steppable():
    for x in xrange(100):
        yield
        print x

@coroutine
def steppable2():
    for y in ['a','b','c']:
        x = steppable()
        while step(x): yield
        print y

#step(steppable(),50)
#step(steppable(),-1)
x = steppable2()

while step(x): pass




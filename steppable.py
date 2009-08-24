#!/usr/bin/env python

from coroutine import coroutine


@coroutine
def steppable():
    for x in xrange(100):
        yield
        print x

def step(x,steps=1):
    try:
        if steps >= 0:
            for i in xrange(steps):
                x.next()
        else:
            while True:
                x.next()
        return True
    except StopIteration:
        return False


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




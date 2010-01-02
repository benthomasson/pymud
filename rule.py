#!/usr/bin/env python

import unittest
from pymud.chainedmap import ChainedMap

def Pass(self,o):
    return True

def Fail(self,o):
    return False

def NullAction(self,o):
    pass

class Rule(object):

    def __init__(self,condition=Fail,action=NullAction):
        self.condition = condition
        self.action = action

    def __call__(self,o):
        if self.condition(self,o):
            self.action(self,o)

class Struct(object): pass

class StopException(Exception): pass

def rcmp(x,y):
    xN,ignore,xLabel = x.partition('_')
    yN,ignore,yLabel = y.partition('_')
    v = cmp(xN,yN)
    if v: return v
    return cmp(xLabel,yLabel)

def runRules(o,rules):
    try:
        for rule in rules:
            rule(o)
    except StopException, e:
        pass

class Action(object):

    rules = ChainedMap(map={})

    def __call__(self):
        runRules(self,self.rules)

class _TestRules(unittest.TestCase):

    def testNull(self):
        x = Rule()
        o = Struct()
        x(o)

    def testSimple(self):
        def c(self,o):
            return True
        def a(self,o):
            o.a = 5
        x = Rule(c,a)
        o = Struct()
        x(o)
        self.assert_(hasattr(o,'a'))
        self.assertEquals(o.a, 5)

    def testRules(self):
        def c(self,o):
            return True
        def a(self,o):
            o.a = 5
        def b(self,o):
            o.a = 4
        def s(self,o):
            raise StopException()
        x1 = Rule(c,a)
        x2 = Rule(c,b)
        x3 = Rule(c,s)
        o = Struct()
        runRules(o,[x1,x2])
        self.assertEquals(o.a, 4)
        o = Struct()
        runRules(o,[x1,x2])
        self.assertEquals(o.a, 4)
        o = Struct()
        runRules(o,[x2,x1])
        self.assertEquals(o.a, 5)
        o = Struct()
        runRules(o,[x2,x3,x1])
        self.assertEquals(o.a, 4)
    
class _TestAction(unittest.TestCase):

    def testBase(self):
        a = Action()
        a()

    def testSimple(self):
        def c(self,o):
            return True
        def a(self,o):
            o.a = 5
        def b(self,o):
            o.a = 4
        def s(self,o):
            raise StopException()
        x1 = Rule(c,a)
        x2 = Rule(c,b)
        x3 = Rule(c,s)
        a = Action()
        a.rules = [x2,x3,x1]
        a()
        self.assertEquals(a.a, 4)

if __name__ == "__main__":
    unittest.main()


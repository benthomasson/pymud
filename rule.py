#!/usr/bin/env python

import unittest
from pymud.chainedmap import ChainedMap
from pymud.coroutine import step, finish

def Pass(rule,o):
    return True

def Fail(rule,o):
    return False

def NullAction(rule,o):
    pass

class Rule(object):

    def __init__(self,condition=Fail,action=NullAction):
        self.condition = condition
        self.action = action

    def __call__(self,o):
        if self.condition(self,o):
            self.action(self,o)

class SteppableRule(Rule):

    def __call__(self,o):
        if self.condition(self,o):
            call = self.action(self,o)
            while step(call): yield

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
        def c(rule,o):
            return True
        def a(rule,o):
            o.a = 5
        x = Rule(c,a)
        o = Struct()
        x(o)
        self.assert_(hasattr(o,'a'))
        self.assertEquals(o.a, 5)

    def testRules(self):
        def c(rule,o):
            return True
        def a(rule,o):
            o.a = 5
        def b(rule,o):
            o.a = 4
        def s(rule,o):
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
        def c(rule,o):
            return True
        def a(rule,o):
            o.a = 5
        def b(rule,o):
            o.a = 4
        def s(rule,o):
            raise StopException()
        x1 = Rule(c,a)
        x2 = Rule(c,b)
        x3 = Rule(c,s)
        a = Action()
        a.rules = [x2,x3,x1]
        a()
        self.assertEquals(a.a, 4)

class _TestSteppableRule(unittest.TestCase):

    def test(self):
        def a(rule,o):
            return iter(xrange(5))
        o = Struct()
        call = SteppableRule(Pass,a)(o)
        finish(call)

    def test2(self):
        def a(rule,o):
            o.x = 0
            call = iter(xrange(5))
            while step(call):
                o.x += 1
                yield
        o = Struct()
        call = SteppableRule(Pass,a)(o)
        self.assert_(step(call))
        self.assertEquals(o.x,1)
        self.assert_(step(call))
        self.assertEquals(o.x,2)
        self.assert_(step(call))
        self.assertEquals(o.x,3)
        self.assert_(step(call))
        self.assertEquals(o.x,4)
        self.assert_(step(call))
        self.assertEquals(o.x,5)
        self.assertFalse(step(call))
        self.assertEquals(o.x,5)

if __name__ == "__main__":
    unittest.main()


#!/usr/bin/env python

import unittest

def Fail(self,o):
    return False

def NullAction(self,o):
    pass

class Rule(object):

    def __init__(self):
        self.condition = Fail
        self.action = NullAction

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

def runRules(o,ruleMap):
    try:
        for key in sorted(ruleMap.keys(),cmp=rcmp):
            ruleMap[key](o)
    except StopException, e:
        pass

class Test(unittest.TestCase):

    def testNull(self):
        x = Rule()
        o = Struct()
        x(o)

    def testSimple(self):
        x = Rule()
        def c(self,o):
            return True
        def a(self,o):
            o.a = 5
        x.condition = c
        x.action = a
        o = Struct()
        x(o)
        self.assert_(hasattr(o,'a'))
        self.assertEquals(o.a, 5)

    def testRules(self):
        from pymud.chainedmap import ChainedMap
        x1, x2, x3 = Rule(), Rule(), Rule()
        def c(self,o):
            return True
        def a(self,o):
            o.a = 5
        def b(self,o):
            o.a = 4
        def s(self,o):
            raise StopException()
        x1.condition,x1.action = c,a
        x2.condition,x2.action = c,b
        x3.condition,x3.action = c,s
        o = Struct()
        m = ChainedMap(map={'10':x2,'1':x1})
        runRules(o,m)
        self.assertEquals(o.a, 4)
        o = Struct()
        m = ChainedMap(map={'10_b':x2,'1_a':x1})
        runRules(o,m)
        self.assertEquals(o.a, 4)
        o = Struct()
        m = ChainedMap(map={'1_a':x2,'1_b':x1})
        runRules(o,m)
        self.assertEquals(o.a, 5)
        o = Struct()
        m = ChainedMap(map={'1_a':x2,'1_b':x3,'1_c':x1})
        runRules(o,m)
        self.assertEquals(o.a, 4)
    

if __name__ == "__main__":
    unittest.main()


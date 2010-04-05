#!/usr/bin/env python

import unittest
from pymud.chainedmap import ChainedMap
from pymud.coroutine import step, finish
from types import GeneratorType

class Condition(object): pass
class Action(object): pass

class _Pass(Condition):
    "Pass"

    def __call__(self,rule,o):
        return True

Pass = _Pass()

class _Fail(Condition):
    "Fail"

    def __call__(self,rule,o):
        return False

Fail = _Fail()

class _NullAction(Action):
    "Do nothing"

    def __call__(self,rule,o,result):
        pass

NullAction = _NullAction()

class Rule(object):

    def __init__(self,condition=Fail,
                      action=NullAction,
                      failAction=NullAction):
        self.condition = condition
        self.action = action
        self.failAction = failAction

    def __call__(self,o):
        result = self.condition(self,o)
        if result:
            self.action(self,o,result)
        else:
            self.failAction(self,o,result)

class SteppableRule(Rule):

    def __call__(self,o):
        if self.condition(self,o):
            call = self.action(self,o)
            if isinstance(call,GeneratorType):
                while step(call): yield
        else:
            self.failAction(self,o)

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

#Conditions

class Not(Condition):
    "Not"

    def __init__(self,fn):
        self.fn = fn

    def __call__(self,rule,o):
        return not self.fn(rule,o)

class And(Condition):
    "And"

    def __init__(self,*fns):
        self.fns = fns

    def __call__(self,rule,o):
        for fn in self.fns:
            if not fn(rule,o):
                return False
        return True

class Or(Condition):
    "Or"

    def __init__(self,*fns):
        self.fns = fns

    def __call__(self,rule,o):
        for fn in self.fns:
            if fn(rule,o):
                return True
        return False


#Actions

class ProgN(Action):
    "Do multiple actions"

    def __init__(self,*fns):
        self.fns = fns

    def __call__(self,rule,o,result):
        "Do multiple actions"
        last = None
        for fn in self.fns:
            last = fn(rule,o,result)
        return last

class StopAction(Action):
    "Stop running rules"

    def __call__(self,rule,o,result):
        raise StopException()

class CallRuleAction(Action):
    "Call another rule"

    def __init__(self,callRule):
        self.callRule = callRule

    def __call__(self,rule,o,result):
        self.callRule(o)

class CallRuleListAction(Action):
    "Call another rule set"

    def __init__(self,rules):
        self.rules = rules

    def __call__(self,rule,o,result):
        runRules(o,self.rules)

class _TestRules(unittest.TestCase):

    def testNull(self):
        x = Rule()
        o = Struct()
        x(o)

    def testSimple(self):
        def c(rule,o):
            return True
        def a(rule,o,result):
            o.a = 5
        x = Rule(c,a)
        o = Struct()
        x(o)
        self.assert_(hasattr(o,'a'))
        self.assertEquals(o.a, 5)

    def testRules(self):
        def c(rule,o):
            return True
        def a(rule,o,result):
            o.a = 5
        def b(rule,o,result):
            o.a = 4
        def s(rule,o,result):
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


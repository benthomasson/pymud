#!/usr/bin/env python

import unittest
import random

def weighted_choices(d):
    normalized = {}
    keys = []
    current = 0
    for value,weight in d.iteritems():
        keys.append(current)
        normalized[current] = value
        current += weight
    weightSum = current
    print normalized
    while True:
        i = random.randint(0,weightSum)
        choice = None
        for key in keys:
            if key > i: break
            choice = key
        if choice in normalized:
            yield normalized[choice]
        else:
            yield None

class _Test(unittest.TestCase):

    def test(self):
        ite = weighted_choices({})
        self.assertFalse(ite.next())

    def test2(self):
        ite = weighted_choices({})
        self.assertFalse(ite.next())
        self.assertFalse(ite.next())

    def testSingle(self):
        ite = weighted_choices({'a':1})
        self.assertEquals(ite.next(),'a')
        self.assertEquals(ite.next(),'a')
        self.assertEquals(ite.next(),'a')
        self.assertEquals(ite.next(),'a')
        self.assertEquals(ite.next(),'a')

    def testTwo(self):
        ite = weighted_choices({'a':1,'b':1})
        foundA,foundB = False, False
        for x in xrange(100):
            choice = ite.next()
            if choice is 'a': foundA = True
            if choice is 'b': foundB = True
            self.assert_(choice is 'a' or choice is 'b')
        self.assert_(foundA)
        self.assert_(foundB)

    def testThree(self):
        ite = weighted_choices({'a':100,'b':100,'c':1})
        foundA,foundB,foundC = False, False, False
        for x in xrange(10000):
            choice = ite.next()
            if choice is 'a': foundA = True
            if choice is 'b': foundB = True
            if choice is 'c': foundC = True
            self.assert_(choice is 'a' or choice is 'b' or choice is 'c')
        self.assert_(foundA)
        self.assert_(foundB)
        self.assert_(foundC)

if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python

import unittest

class Null(object):

    def __getattribute__(self,name):
        return self

    def __nonzero__(self):
        return False

    def __eq__(self,other):
        return other == None
        
    def __call__(self,*args,**kwargs):
        return self

null = Null()

class Test(unittest.TestCase):

    def testNoneEquivalence(self):
        self.assertFalse(None)
        self.assertFalse(null)
        self.assert_(null == None)
        self.assertFalse(null == True)
        self.assertFalse(null == False)

    def testIgnoreMethods(self):
        self.assertFalse(null.notAMethod(1,2,3,5))

    def testAssignment(self):
        null.x = 5
        self.assertFalse(null.x())
        self.assertFalse(null.x)

    def testCall(self):
        self.assertFalse(null())

    def testChainedMethods(self):
        self.assertFalse(null.x(1,2,3).y(4,5,7).z())

if __name__ == '__main__':
    unittest.main()

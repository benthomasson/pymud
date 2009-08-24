#!/usr/bin/env python

import unittest
from mob import Mob

class Test(unittest.TestCase):

    def testMobExec(self):
        mob = Mob()
        mob._commands['do'] = mob.do
        mob.mobExec("print 1 + 1")
        mob.mobExec(\
"""if 1:
    print 1 + 1""")
        mob.mobExec("do()")

    def testMobEval(self):
        mob = Mob()
        mob._commands['do'] = mob.do
        self.assertEquals(mob.mobEval("1 + 1"),2)
        mob.mobEval('do()')

if __name__ == '__main__':
    unittest.main()


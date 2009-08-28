#!/usr/bin/env python

import unittest

import shelve
import mob 
import sys

class Test(unittest.TestCase):

    def testSimple(self):
        s = shelve.open("test",protocol=2)
        s['a'] = 1
        s.close()
        s = shelve.open("test",protocol=2)
        self.assertEquals(s['a'],1)
        s.close()

    def test(self):
        m = mob.Mob()
        m.applyCommand("say",["hi"])

    def testMob(self):
        s = shelve.open("test",protocol=2)
        m = mob.Mob()
        m.applyCommand("say",["hi"])
        s['a'] = m
        s.close()
        s = shelve.open("test",protocol=2)
        m = s['a']
        m.stdout = sys.stdout
        m.applyCommand("say",["hi"])
        self.assert_(s['a'])
        s.close()

if __name__ == "__main__":
    unittest.main()

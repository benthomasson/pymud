#!/usr/bin/env python

import unittest

import shelve
import mob 
import sys

class Persistence(object):

    def __init__(self,filename):
        self.db = shelve.open(filename,protocol=2)

    def persist(self,o):
        self.db[o.id] = o

    def get(self,id):
        return self.db[id]

    def sync(self):
        self.db.sync()

    def close(self):
        self.db.close()


class TestShelve(unittest.TestCase):

    def testSimple(self):
        s = shelve.open("test.db",protocol=2)
        s['a'] = 1
        s.close()
        s = shelve.open("test.db",protocol=2)
        self.assertEquals(s['a'],1)
        s.close()

    def test(self):
        m = mob.Mob()
        m.applyCommand("say",["hi"])

    def testMob(self):
        s = shelve.open("test.db",protocol=2)
        m = mob.Mob()
        m.applyCommand("say",["hi"])
        s['a'] = m
        s.close()
        s = shelve.open("test.db",protocol=2)
        m = s['a']
        m.stdout = sys.stdout
        m.applyCommand("say",["hi"])
        self.assert_(s['a'])
        s.close()

class TestPersistence(unittest.TestCase):

    def testMob(self):
        p = Persistence("test.db")
        mob.Mob.id = 0
        m = mob.Mob()
        m.applyCommand("say",["hi"])
        p.persist(m)
        p.close()
        p = Persistence("test.db")
        m = p.get('0')
        m.stdout = sys.stdout
        m.applyCommand("say",["hi"])
        p.close()

if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python

import unittest

import shelve
import sys
import os
from coroutine import coroutine,step


class Persistence(object):

    def __init__(self,filename):
        self.db = shelve.open(filename,protocol=2,writeback=True)
        self.writeBackQueue = None
        if '0' in self.db:
            self.id = self.db['0']
        else:
            self.id = 0
        self.db['0'] = self.id

    def getNextId(self):
        self.id += 1
        self.db['0'] = self.id
        return self.id

    def persist(self,o):
        if not o.id:
            o.id = "%x" % self.getNextId()
        self.db[o.id] = o

    def get(self,id):
        return self.db[id]

    def sync(self,n=10):
        if self.writeBackQueue:
            if not step(self.writeBackQueue,n):
                self.writeBackQueue = None
                return True
            return False
        else:
            self.writeBackQueue = self.partialSync()
            return self.sync()

    @coroutine
    def partialSync(self):
        db = self.db
        for key, entry in db.cache.iteritems():
            yield
            db.writeback = False
            print "Persisting %s" % key
            db[key] = entry
            db.writeback = True

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
        import mob 
        m = mob.Mob()
        m.applyCommand("say",["hi"])

    def testMob(self):
        import mob 
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

    def setUp(self):
        os.remove("test.db")

    def testMob(self):
        import mob 
        p = Persistence("test.db")
        self.assertEquals(p.id,0)
        m = mob.Mob()
        m.applyCommand("say",["hi"])
        p.persist(m)
        p.close()
        p = Persistence("test.db")
        self.assertEquals(p.id,1)
        m = p.get('1')
        m.stdout = sys.stdout
        m.applyCommand("say",["hi"])
        p.close()

    def testSync(self):
        import mob 
        p = Persistence("test.db")
        self.assertEquals(p.id,0)
        for x in xrange(100):
            m = mob.Mob()
            m.applyCommand("say",["hi"])
            p.persist(m)
        for x in xrange(10):
            print p.sync()
        p.close()
        p = Persistence("test.db")
        self.assertEquals(p.id,100)
        m = p.get('1')
        m.stdout = sys.stdout
        m.applyCommand("say",["hi"])
        p.sync()
        p.close()

if __name__ == "__main__":
    unittest.main()

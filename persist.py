#!/usr/bin/env python

import unittest

import shelve
import sys
import os
from coroutine import coroutine,step

persist = None

class P(object):
    """"""

    def __init__(self,o):
        self.id = o.id
        self.ref = o

    def __call__(self):
        if self.ref:
            return self.ref
        if not self.id: return None
        try:
            return persist.get(self.id)
        except KeyValue,e:
            return None

    def __setstate__(self,state):
        self.id = state['id']

    def __getstate__(self):
        state = {}
        state['id'] = self.id
        return state

class Persistence(object):

    def __init__(self,filename):
        self.db = shelve.open(filename,protocol=2,writeback=True)
        self.writeBackIterator = None
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
        return o

    def get(self,id):
        return self.db[id]

    def sync(self,n=1):
        if not self.writeBackIterator:
            self.writeBackIterator = self.partialSync()
        if not step(self.writeBackIterator,n):
            self.writeBackIterator = None
            return True
        return False

    @coroutine
    def partialSync(self):
        db = self.db
        for key, entry in db.cache.iteritems():
            yield
            db.writeback = False
            print "Persisting %s" % key
            db[key] = entry
            db.writeback = True

    def run(self,n=1):
        self.sync(n)

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
        global persist
        if os.path.exists("test.db"): os.remove("test.db")
        persist = None

    def testMob(self):
        global persist
        import mob 
        persist = Persistence("test.db")
        self.assertEquals(persist.id,0)
        m = mob.Mob()
        m.applyCommand("say",["hi"])
        persist.persist(m)
        persist.close()
        persist = Persistence("test.db")
        self.assertEquals(persist.id,1)
        m = persist.get('1')
        m.stdout = sys.stdout
        m.applyCommand("say",["hi"])
        persist.close()

    def testSync(self):
        import mob 
        persist = Persistence("test.db")
        self.assertEquals(persist.id,0)
        for x in xrange(100):
            m = mob.Mob()
            m.applyCommand("say",["hi"])
            persist.persist(m)
        for x in xrange(10):
            print persist.sync()
        persist.close()
        persist = Persistence("test.db")
        self.assertEquals(persist.id,100)
        m = persist.get('1')
        m.stdout = sys.stdout
        m.applyCommand("say",["hi"])
        persist.sync()
        persist.close()

class TestP(unittest.TestCase):

    def setUp(self):
        global persist
        if os.path.exists("test.db"): os.remove("test.db")
        persist = None

    def testTemporary(self):
        import mob
        import sys
        global persist
        m = P(mob.Mob())
        self.assert_(m())
        self.assertFalse(m().id)
        m().stdout = sys.stdout
        m().run()
        m().applyCommand("say",['testTemporary'])
        m.ref = None
        self.assertFalse(m())

    def testPersistent(self):
        import mob
        import sys
        global persist
        persist = Persistence("test.db")
        m = P(persist.persist(mob.Mob()))
        self.assert_(m())
        self.assert_(m().id)
        m().stdout = sys.stdout
        m().run()
        m().applyCommand("say",['testPersistent'])
        m.ref = None
        self.assert_(m())
        self.assert_(m().id)
        m().stdout = sys.stdout
        m().run()
        m().applyCommand("say",['testPersistent'])
        persist.close()
        m.ref = None
        persist = Persistence("test.db")
        self.assert_(m())
        self.assert_(m().id)
        m().stdout = sys.stdout
        m().run()
        m().applyCommand("say",['testPersistent'])

if __name__ == "__main__":
    unittest.main()

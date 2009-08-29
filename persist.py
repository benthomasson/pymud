#!/usr/bin/env python

import unittest

import shelve
import sys
import os
from pymud.coroutine import coroutine,step

persist = None

class P(object):
    """P is a persistent reference to a persistent object.
    To create a new persistent reference use:
    
    >>> x = persist.P(o).

    To retrieve the object from the peristent reference above use:

    >>> x()
    """

    def __init__(self,o):
        self.id = o.id
        self.ref = o

    def __call__(self):
        if self.ref and not self.ref.deleted:
            return self.ref
        if self.ref and self.ref.deleted:
            return None
        if not self.id: return None
        try:
            return persist.get(self.id)
        except KeyError,e:
            return None

    def delete(self):
        persist.delete(self)
        self.id = None
        self.ref = None

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

    def delete(self,o):
        if o.id in self.db:
            self.db[o.id].deleted = True
            del self.db[o.id]

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
        for key, entry in db.cache.copy().iteritems():
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

    def testSyncDelete(self):
        import mob 
        persist = Persistence("test.db")
        self.assertEquals(persist.id,0)
        for x in xrange(100):
            m = mob.Mob()
            m.applyCommand("say",["hi"])
            persist.persist(m)
        persist.sync()
        persist.delete(m)
        for x in xrange(10):
            print persist.sync()
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

    def testDeletedPersistent(self):
        import mob
        import sys
        global persist
        persist = Persistence("test.db")
        m = P(persist.persist(mob.Mob()))
        m().run()
        persist.delete(m)
        self.assertTrue(m.ref.deleted)
        self.assertFalse(m())
        m.ref = None
        persist.close()
        persist = Persistence("test.db")
        self.assertFalse(m())

    def testDelete(self):
        import mob
        import sys
        global persist
        persist = Persistence("test.db")
        m = P(persist.persist(mob.Mob()))
        m().run()
        m.delete()
        self.assertFalse(m())
        m.delete()
        self.assertFalse(m())
        persist.close()
        persist = Persistence("test.db")
        self.assertFalse(m())

if __name__ == "__main__":
    unittest.main()

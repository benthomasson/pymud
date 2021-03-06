#!/usr/bin/env python

import unittest

import shelve
import sys
import os
from pymud.coroutine import coroutine,step,finish
from pymud.formatter import ColorTextFormatter

def getP(o):
    if o.id in P.instances:
        return P.instances[o.id]
    else:
        p = P(o)
        P.instances[o.id] = p
        return p

class P(object):
    """P is a persistent reference to a persistent object.
    To create a new persistent reference use:
    
    >>> x = persist.P(o).

    To retrieve the object from the persistent reference above use:

    >>> x()
    """

    persist = None
    instances = {}

    __slots__ = ['id','ref']

    def __init__(self,o=None):
        if not o:
            self.id = None
            self.ref = None
        elif isinstance(o,P):
            self.id = o.id
            self.ref = o()
        else:
            self.id = o.id
            self.ref = o
        P.instances[self.id] = self

    def __call__(self):
        if self.ref and not hasattr(self.ref,'deleted'):
            return self.ref
        if self.ref and not self.ref.deleted:
            return self.ref
        if self.ref and self.ref.deleted:
            return None
        if not self.id: return None
        try:
            self.ref = P.persist.get(self.id)
            return self.ref
        except KeyError,e:
            return None

    def __eq__(self,other):
        return self.id == other.id

    def __nonzero__(self):
        return self() != None

    def delete(self):
        del P.instances[self.id]
        P.persist.delete(self)
        self.id = None
        self.ref = None

    def __setstate__(self,state):
        self.id = state['id']
        self.ref = None

    def __getstate__(self):
        state = {}
        state['id'] = self.id
        return state

    def __str__(self):
        return "P" + str(self())

    def __repr__(self):
        return "P" + repr(self())

P.null = P()

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

    def getOrCreate(self,id,klass,*args,**kwargs):
        if self.exists(id):
            return self.get(id)
        else:
            instance = klass(id=id,*args,**kwargs)
            instance.id = id
            self.persist(instance)
            return instance

    def exists(self,id):
        try:
            self.db[id]
            return True
        except KeyError, e:
            return False

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

    def syncAll(self):
        if not self.writeBackIterator:
            self.writeBackIterator = self.partialSync()
        finish(self.writeBackIterator)
        self.db.dict.sync()

    @coroutine
    def partialSync(self):
        db = self.db
        for key, entry in db.cache.copy().iteritems():
            yield
            db.writeback = False
            #print "Persisting %s" % key
            db[key] = entry
            db.writeback = True

    def run(self,n=1):
        self.sync(n)

    def close(self):
        self.db.close()

class MockPersistence(Persistence):

    def __init__(self):
        self.db = {}
        if '0' in self.db:
            self.id = self.db['0']
        else:
            self.id = 0
        self.db['0'] = self.id

    def sync(self,n=1):
        pass

    def syncAll(self):
        pass

    @coroutine
    def partialSync(self):
        yield

    def close(self):
        self.db = None
        self.id = None

class Persistent(object):

    def __init__(self):
        self.id = None
        self.deleted = False

class StdoutReceiver(ColorTextFormatter):

    def __init__(self):
        self.id = None

    def receiveMessage(self,message):
        sys.stdout.write("\n")
        sys.stdout.write(self.formatMessage(message))
        sys.stdout.write("\n")
        sys.stdout.flush()


class TestShelve(unittest.TestCase):

    def setUp(self):
        if os.path.exists("test.db"): os.remove("test.db")
        if os.path.exists("test.db.db"): os.remove("test.db.db")

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
        m.addListener(StdoutReceiver())
        print m.listeners
        m.applyCommand("say",["hi"])
        s['a'] = m
        s.close()
        s = shelve.open("test.db",protocol=2)
        m = s['a']
        m.addListener(StdoutReceiver())
        m.applyCommand("say",["hi"])
        self.assert_(s['a'])
        s.close()

class TestPersistence(unittest.TestCase):

    def setUp(self):
        if os.path.exists("test.db"): os.remove("test.db")
        if os.path.exists("test.db.db"): os.remove("test.db.db")
        P.persist = None
        self.id = None

    def testMob(self):
        import mob 
        P.persist = Persistence("test.db")
        self.assertEquals(P.persist.id,0)
        m = mob.Mob()
        m.addListener(StdoutReceiver())
        m.applyCommand("say",["hi"])
        P.persist.persist(m)
        P.persist.close()
        P.persist = Persistence("test.db")
        self.assertEquals(P.persist.id,1)
        m = P.persist.get('1')
        m.addListener(StdoutReceiver())
        m.applyCommand("say",["hi"])
        P.persist.close()

    def testSync(self):
        import mob 
        P.persist = Persistence("test.db")
        self.assertEquals(P.persist.id,0)
        for x in xrange(100):
            m = mob.Mob()
            m.addListener(StdoutReceiver())
            m.applyCommand("say",["hi"])
            P.persist.persist(m)
        for x in xrange(10):
            print P.persist.sync()
        P.persist.close()
        P.persist = Persistence("test.db")
        self.assertEquals(P.persist.id,100)
        m = P.persist.get('1')
        m.addListener(StdoutReceiver())
        m.applyCommand("say",["hi"])
        P.persist.sync()
        P.persist.close()

    def testSyncDelete(self):
        import mob 
        P.persist = Persistence("test.db")
        self.assertEquals(P.persist.id,0)
        for x in xrange(100):
            m = mob.Mob()
            m.addListener(StdoutReceiver())
            m.applyCommand("say",["hi"])
            P.persist.persist(m)
        P.persist.sync()
        P.persist.delete(m)
        for x in xrange(10):
            print P.persist.sync()
        P.persist.close()

    def testGetOrCreate(self):
        import mob 
        P.persist = Persistence("test.db")
        x = P.persist.getOrCreate("mob",mob.Mob)
        x.nameAttribute = "bob"
        P.persist.close()
        P.persist = Persistence("test.db")
        x = P.persist.getOrCreate("mob",mob.Mob)
        y = P.persist.getOrCreate("notmob",mob.Mob)
        self.assertEquals(x.nameAttribute,"bob")
        self.assertRaises(AttributeError,lambda: y.nameAttribute)
        P.persist.close()

class TestP(unittest.TestCase):

    def setUp(self):
        if os.path.exists("test.db"): os.remove("test.db")
        if os.path.exists("test.db.db"): os.remove("test.db.db")
        P.persist = None

    def testTemporary(self):
        import mob
        import sys
        m = P(mob.Mob())
        self.assert_(m())
        self.assertFalse(m().id)
        m().run(0)
        m().addListener(StdoutReceiver())
        m().applyCommand("say",['testTemporary'])
        m.ref = None
        self.assertFalse(m())

    def testPersistent(self):
        import mob
        import sys
        P.persist = Persistence("test.db")
        m = P(P.persist.persist(mob.Mob()))
        self.assert_(m())
        self.assert_(m.id)
        self.assert_(m.ref)
        self.assertEquals(m().__class__,mob.Mob)
        self.assert_(m().id)
        print m()
        m().run(0)
        m().addListener(StdoutReceiver())
        m().applyCommand("say",['testPersistent'])
        m.ref = None
        self.assert_(m())
        self.assert_(m.id)
        self.assert_(m.ref)
        self.assertEquals(m().__class__,mob.Mob)
        self.assert_(m().id)
        print m()
        m().run(0)
        m().applyCommand("say",['testPersistent'])
        P.persist.close()
        m.ref = None
        P.persist = Persistence("test.db")
        self.assert_(m())
        self.assert_(m.id)
        self.assert_(m.ref)
        self.assertEquals(m().__class__,mob.Mob)
        self.assert_(m().id)
        m().addListener(StdoutReceiver())
        m().run(0)
        m().applyCommand("say",['testPersistent'])

    def testDeletedPersistent(self):
        import mob
        import sys
        P.persist = Persistence("test.db")
        m = P(P.persist.persist(mob.Mob()))
        m().run(0)
        P.persist.delete(m)
        self.assertTrue(m.ref.deleted)
        self.assertFalse(m())
        m.ref = None
        P.persist.close()
        P.persist = Persistence("test.db")
        self.assertFalse(m())

    def testDelete(self):
        import mob
        import sys
        P.persist = Persistence("test.db")
        m = P(P.persist.persist(mob.Mob()))
        m().run(0)
        m.delete()
        self.assertFalse(m())
        m.delete()
        self.assertFalse(m())
        P.persist.close()
        P.persist = Persistence("test.db")
        self.assertFalse(m())

    def testPersistentChain(self):
        import mob
        import sys
        P.persist = Persistence("test.db")
        m = P(P.persist.persist(mob.Mob()))
        m2 = P(m)
        self.assert_(m.ref is m2.ref)

    def testEquality(self):
        self.p1 = P()
        self.p1.id = 5
        self.p1.ref = 9908
        self.p2 = P()
        self.p2.id = 5
        self.p1.ref = 4353
        self.assertEqual(self.p1,self.p2)
        self.assertFalse(self.p1 is self.p2)

    def testList(self):
        self.testEquality()
        l = [self.p2]
        self.assert_(self.p1 in l)
        self.assert_(self.p2 in l)
        l.remove(self.p1)
        self.assertFalse(l)

    def testSame(self):
        import mob
        import sys
        P.persist = Persistence("test.db")
        m = P.persist.persist(mob.Mob())
        p1 = getP(m)
        p2 = getP(m)
        self.assertEquals(p1,p2)
        self.assert_(p1 is p2)

class TestMockPersistence(unittest.TestCase):

    def setUp(self):
        P.persist = None

    def testSame(self):
        import mob
        import sys
        P.persist = MockPersistence()
        m = P.persist.persist(mob.Mob())
        p1 = getP(m)
        p2 = getP(m)
        self.assertEquals(p1,p2)
        self.assert_(p1 is p2)

if __name__ == "__main__":
    unittest.main()

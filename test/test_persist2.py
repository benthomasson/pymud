
import unittest

import shelve
import redis
import pickle
import sys
import os
from pymud.coroutine import coroutine,step,finish
from pymud.formatter import ColorTextFormatter

from pymud.persist2 import Persistence, P, MockPersistence, getP, RedisShelve

def pytest_funcarg__redis_conn(request):
    r = redis.Redis(db=1)
    r.flushdb()
    return r

def test_redis(redis_conn):
    redis_conn.set('a','1')
    assert redis_conn.get('a') == '1'

def test_redis2(redis_conn):
    redis_conn.set('a','1')
    assert redis_conn.get('a') == '1'

def test_mob():
    import mob 
    m = mob.Mob()
    m.applyCommand("say",["hi"])

def test_mob_persist(redis_conn):
    import mob 
    m = mob.Mob()
    m.id = 'a'
    m.addListener(StdoutReceiver())
    print m.listeners
    m.applyCommand("say",["hi"])
    redis_conn.set('a',pickle.dumps(m))
    #print redis_conn.get('a')
    print pickle.loads(redis_conn.get('a'))
    m = pickle.loads(redis_conn.get('a'))
    m.addListener(StdoutReceiver())
    m.applyCommand("say",["hi"])
    assert redis_conn.get('a')

class StdoutReceiver(ColorTextFormatter):

    def __init__(self):
        self.id = None

    def receiveMessage(self,message):
        sys.stdout.write("\n")
        sys.stdout.write(self.formatMessage(message))
        sys.stdout.write("\n")
        sys.stdout.flush()

class TestPersistence(unittest.TestCase):

    def setUp(self):
        P.persist = None
        self.id = None
        redis.Redis(db=1).flushdb()
        RedisShelve.shelves = {}

    def testMob(self):
        import mob 
        P.persist = Persistence(db=1)
        print P.persist.id
        self.assertEquals(P.persist.id,0)
        m = mob.Mob()
        m.addListener(StdoutReceiver())
        m.applyCommand("say",["hi"])
        P.persist.persist(m)
        P.persist = Persistence(db=1)
        self.assertEquals(P.persist.id,1)
        m = P.persist.get('1')
        m.addListener(StdoutReceiver())
        m.applyCommand("say",["hi"])

    def testSync(self):
        import mob 
        P.persist = Persistence(db=1)
        print P.persist.id
        self.assertEquals(P.persist.id,0)
        for x in xrange(100):
            m = mob.Mob()
            m.addListener(StdoutReceiver())
            m.applyCommand("say",["hi"])
            P.persist.persist(m)
        for x in xrange(10):
            print P.persist.sync()
        P.persist = Persistence(db=1)
        self.assertEquals(P.persist.id,100)
        m = P.persist.get('1')
        m.addListener(StdoutReceiver())
        m.applyCommand("say",["hi"])
        P.persist.sync()

    def testSyncDelete(self):
        import mob 
        P.persist = Persistence(db=1)
        print P.persist.id
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

    def testGetOrCreate(self):
        import mob 
        P.persist = Persistence(db=1)
        x = P.persist.getOrCreate("mob",mob.Mob)
        x.nameAttribute = "bob"
        P.persist = Persistence(db=1)
        x = P.persist.getOrCreate("mob",mob.Mob)
        y = P.persist.getOrCreate("notmob",mob.Mob)
        self.assertEquals(x.nameAttribute,"bob")
        self.assertRaises(AttributeError,lambda: y.nameAttribute)

class TestP(unittest.TestCase):

    def setUp(self):
        P.persist = None
        redis.Redis(db=1).flushdb()
        

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
        P.persist = Persistence(db=1)
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
        m.ref = None
        P.persist = Persistence(db=1)
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
        P.persist = Persistence(db=1)
        m = P(P.persist.persist(mob.Mob()))
        m().run(0)
        P.persist.delete(m)
        self.assertTrue(m.ref.deleted)
        self.assertFalse(m())
        m.ref = None
        P.persist = Persistence(db=1)
        self.assertFalse(m())

    def testDelete(self):
        import mob
        import sys
        P.persist = Persistence(db=1)
        m = P(P.persist.persist(mob.Mob()))
        m().run(0)
        m.delete()
        self.assertFalse(m())
        m.delete()
        self.assertFalse(m())
        P.persist = Persistence(db=1)
        self.assertFalse(m())

    def testPersistentChain(self):
        import mob
        import sys
        P.persist = Persistence(db=1)
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
        P.persist = Persistence(db=1)
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



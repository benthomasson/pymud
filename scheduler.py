#!/usr/bin/env python

import unittest
from pymud.coroutine import coroutine,step
from pymud.persist import P

def gettime():
    return Scheduler.scheduler.tick

def gettimesince(oldtick):
    return Scheduler.scheduler.tick - oldtick

class Scheduler(object):

    scheduler = None
    tick = 0

    def __init__(self,id = None):
        self.items = {}
        self.itemsIterator = None
        self.id = id
        self.tick = 0

    def schedule(self,o):
        self.items[o.id] = P(o)

    def run(self,n=1):
        if not self.items: return True
        if not self.itemsIterator:
            self.itemsIterator =  self.runItems()
        if not step(self.itemsIterator,n):
            self.itemsIterator = None
            self.tick += n
            return True
        return False

    @coroutine
    def runItems(self):
        for key, entry in self.items.copy().iteritems():
            yield
            if entry(): 
                if hasattr(entry(),"run"):
                    entry().run()
                else:
                    del self.items[key]
            else:
                del self.items[key]

    def __setstate__(self,state):
        self.__dict__ = state.copy()
        self.itemsIterator = None

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['itemsIterator']
        return state


class Test(unittest.TestCase):

    def testEmpty(self):
        s = Scheduler()
        self.assert_(s.run())

    def testMob(self):
        from pymud.mob import Mob
        s = Scheduler()
        m = Mob()
        m.id = '0'
        s.schedule(m)
        self.assert_(s.run())

    def testMultipleMob(self):
        from pymud.mob import Mob
        s = Scheduler()
        for x in xrange(100):
            m = Mob()
            m.id = '%x' % x
            s.schedule(m)
        self.assert_(s.run(100))

    def testDelete(self):
        from pymud.mob import Mob
        s = Scheduler()
        m = Mob()
        m.id = '0'
        s.schedule(m)
        self.assert_(s.run())
        m.deleted = True
        self.assert_(s.run())

    def testGetTime(self):
        from pymud.mob import Mob
        s = Scheduler()
        m = Mob()
        m.id = '0'
        s.schedule(m)
        Scheduler.scheduler = s
        self.assertEquals(gettime(),0)
        s.run()
        self.assertEquals(gettime(),1)
        s.run(10)
        self.assertEquals(gettime(),11)


if __name__ == "__main__":
    unittest.main()

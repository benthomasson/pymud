#!/usr/bin/env python

import unittest
from pymud.coroutine import coroutine,step
from pymud.persist import P

class Scheduler(object):

    scheduler = None

    def __init__(self):
        self.items = {}
        self.itemsIterator = None
        self.id = None

    def schedule(self,o):
        self.items[o.id] = P(o)

    def run(self,n=1):
        if not self.items: return True
        if not self.itemsIterator:
            self.itemsIterator =  self.runItems()
        if not step(self.itemsIterator,n):
            self.itemsIterator = None
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

if __name__ == "__main__":
    unittest.main()

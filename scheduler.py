#!/usr/bin/env python

import unittest
from coroutine import coroutine,step

class Scheduler(object):

    def __init__(self):
        self.items = {}
        self.itemsIterator = None

    def schedule(self,o):
        self.items[o.id] = o

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
        for key, entry in self.items.iteritems():
            yield
            entry.run()

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
        import mob
        s = Scheduler()
        m = mob.Mob()
        m.id = '0'
        s.schedule(m)
        self.assert_(s.run())

    def testMultipleMob(self):
        import mob
        s = Scheduler()
        for x in xrange(100):
            m = mob.Mob()
            m.id = '%x' % x
            s.schedule(m)
        self.assert_(s.run(100))

    def testPersist(self):
        import mob
        import persist
        pass

if __name__ == "__main__":
    unittest.main()

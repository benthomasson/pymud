#!/usr/bin/env python

import unittest
from pymud.coroutine import coroutine,step,finish
from pymud.persist import P
import time

def gettime():
    return Scheduler.scheduler.tick

def gettimesince(oldtick):
    return Scheduler.scheduler.tick - oldtick

class Scheduler(object):

    scheduler = None
    tick = 0

    def __init__(self,id = None):
        self.items = {}
        self.itemQueues = {}
        self.itemIterators = {}
        self.id = id
        self.tick = 0

    def schedule(self,o):
        queue = o.ticksPerTurn
        for itemQueue in self.itemQueues.values():
            if queue in itemQueue:
                del itemQueue[queue]
        if queue not in self.itemQueues:
            self.itemQueues[queue] = {}
        self.itemQueues[queue][o.id] = P(o)

    def run(self,n=1):
        self.tick += n
        for queue in self.itemQueues.keys():
            if self.tick % queue == 0:
                if queue in self.itemIterators and self.itemIterators[queue]:
                    finish(self.itemIterators[queue])
                    self.itemIterators[queue] = None
                self.itemIterators[queue] = self.runItemQueue(queue)
        for queue,iterator in self.itemIterators.iteritems():
            step(iterator)

        #time.sleep(1)

    def runItemQueue(self,queue):
        items = self.itemQueues[queue].copy()
        count = len(items)
        perTick = count/queue + 1
        index = 0
        for key, entry in items.iteritems():
            index += 1
            if index > perTick:
                index = 0
                yield
            if entry(): 
                entry().run(self.tick)
            else:
                del self.itemQueues[queue][key]

    def __setstate__(self,state):
        self.__dict__ = state.copy()
        self.itemIterators = {}

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['itemIterators']
        return state


class Test(unittest.TestCase):

    def testEmpty(self):
        s = Scheduler()
        s.run()

    def testMob(self):
        from pymud.mob import Mob
        s = Scheduler()
        m = Mob()
        m.id = '0'
        s.schedule(m)
        s.run()

    def testMultipleMob(self):
        from pymud.mob import Mob
        s = Scheduler()
        for x in xrange(100):
            m = Mob()
            m.id = '%x' % x
            s.schedule(m)
        s.run(100)

    def testDelete(self):
        from pymud.mob import Mob
        s = Scheduler()
        m = Mob()
        m.id = '0'
        s.schedule(m)
        s.run()
        m.deleted = True
        s.run()

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

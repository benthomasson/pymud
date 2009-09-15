#!/usr/bin/env python

import unittest
from pymud.persist import P
from pymud.exceptions import *

class Container(object):

    def __init__(self):
        self.containsById = {}

    def remove(self,o):
        self.checkRemove(o)
        if o.id in self.containsById:
            del self.containsById[o.id]


    def add(self,o):
        self.checkHold(o)
        if o.location():
            o.location().remove(o)
        o.location = P(self)
        p = P(o)
        self.containsById[o.id] = p

    def get(self,id=None,attribute=None,index=0):
        if id and id in self.containsById:
            o = self.containsById[id]
            if not o():
                del self.containsById[id]
                raise GameException("Cannot find anything like %s" % attribute)
            else:
                return o
        elif attribute:
            for o in self.containsById.values():
                if o():
                    if attribute == o().name:
                        return o
                    elif attribute in o().attributes:
                        return o
            raise GameException("Cannot find anything like %s" % attribute)
        else:
            raise GameException("Cannot find anything like %s" % attribute)


    def seen(self,o):
        for x in self.containsById.values():
            if x() and x() is not o:
                o.sendMessage("look",description=x().description)

    def checkHold(self,o):
        pass

    def checkRemove(self,o):
        pass

class Test(unittest.TestCase):


    def testSingle(self):
        from mob import Mob
        c = Container()
        c.id = "container"
        m = Mob(id='mob')
        c.add(m)
        self.assertEquals(c.containsById['mob'](), m)
        self.assertEquals(c.get(id='mob')(),m)
        self.assertEquals(c.get(attribute='mob')(),m)
        c.remove(m)
        self.assertFalse('mob' in c.containsById)
        pass

    def testMultiple(self):
        from mob import Mob
        c = Container()
        c.id = "container"
        m1 = Mob(id='mob1')
        m2 = Mob(id='mob2')
        c.add(m1)
        c.add(m2)
        self.assertEquals(c.containsById['mob1'](), m1)
        self.assertEquals(c.get(id='mob1')(),m1)
        self.assertEquals(c.get(id='mob2')(),m2)
        self.assertEquals(c.get(attribute='mob')(),m2)
        c.remove(m1)
        self.assertFalse('mob1' in c.containsById)
        self.assertEquals(c.get(id='mob2')(),m2)
        self.assertEquals(c.get(attribute='mob')(),m2)
        c.remove(m2)
        self.assertFalse('mob2' in c.containsById)
        self.assertRaises(GameException,c.get,attribute='xcvc')
        self.assertRaises(GameException,c.get,attribute='mob')
        pass

if __name__ == "__main__":
    unittest.main()

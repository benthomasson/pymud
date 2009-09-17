#!/usr/bin/env python

import unittest
from pymud.persist import P
from pymud.exceptions import *

class Container(object):

    def __init__(self):
        self.contains = {}

    def remove(self,o):
        self.checkRemove(o)
        if o.id in self.contains:
            del self.contains[o.id]

    def add(self,o):
        self.checkHold(o)
        if o.location():
            o.location().remove(o)
        o.location = P(self)
        p = P(o)
        self.contains[o.id] = p

    def get(self,id=None,attribute=None,index=0):
        if id and id in self.contains:
            o = self.contains[id]
            if not o():
                del self.contains[id]
                raise GameException("Cannot find anything like %s" % attribute)
            else:
                return o
        elif attribute:
            for o in self.contains.values():
                if o():
                    if attribute == o().name:
                        return o
                    elif attribute in o().attributes:
                        return o
            raise GameException("Cannot find anything like %s" % attribute)
        else:
            raise GameException("Cannot find anything like %s" % attribute)


    def seen(self,o):
        for x in self.contains.values():
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
        self.assertEquals(c.contains['mob'](), m)
        self.assertEquals(c.get(id='mob')(),m)
        self.assertEquals(c.get(attribute='mob')(),m)
        c.remove(m)
        self.assertFalse('mob' in c.contains)
        pass

    def testMultiple(self):
        from mob import Mob
        c = Container()
        c.id = "container"
        m1 = Mob(id='mob1')
        m2 = Mob(id='mob2')
        c.add(m1)
        c.add(m2)
        self.assertEquals(c.contains['mob1'](), m1)
        self.assertEquals(c.get(id='mob1')(),m1)
        self.assertEquals(c.get(id='mob2')(),m2)
        self.assertEquals(c.get(attribute='mob')(),m2)
        c.remove(m1)
        self.assertFalse('mob1' in c.contains)
        self.assertEquals(c.get(id='mob2')(),m2)
        self.assertEquals(c.get(attribute='mob')(),m2)
        c.remove(m2)
        self.assertFalse('mob2' in c.contains)
        self.assertRaises(GameException,c.get,attribute='xcvc')
        self.assertRaises(GameException,c.get,attribute='mob')
        pass

if __name__ == "__main__":
    unittest.main()

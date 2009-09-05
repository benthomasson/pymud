#!/usr/bin/env python

import unittest
from pymud.persist import P

class Container(object):

    def __init__(self):
        self.containsById = {}
        self.containsByAttribute = {}

    def remove(self,o):
        if o.id in self.containsById:
            p = self.containsById[o.id]
            del self.containsById[o.id]
            for value in o.attributes.values():
                if value in self.containsByAttribute:
                    self.containsByAttribute[value].remove(p)


    def add(self,o):
        if o.location():
            o.location().remove(o)
        o.location = P(self)
        p = P(o)
        self.containsById[o.id] = p
        for value in o.attributes.values():
            if value in self.containsByAttribute:
                self.containsByAttribute[value].append(p)
            else:
                self.containsByAttribute[value] = [p]

    def get(self,id=None,attribute=None):
        if id and id in self.containsById:
            return self.containsById[id]
        elif attribute and attribute in self.containsByAttribute and\
                self.containsByAttribute[attribute]:
            return self.containsByAttribute[attribute]
        else:
            return None

    def seen(self,o):
        for x in self.containsById.values():
            if x():
                o.sendMessage("look",description=x().description)

class Test(unittest.TestCase):


    def testSingle(self):
        from mob import Mob
        c = Container()
        c.id = "container"
        m = Mob(id='mob')
        c.add(m)
        self.assertEquals(c.containsById['mob'](), m)
        self.assertEquals(c.containsByAttribute['mob'][0](), m)
        self.assertEquals(c.get(id='mob')(),m)
        c.remove(m)
        self.assertFalse('mob' in c.containsById)
        self.assertEquals(c.containsByAttribute['mob'], [])
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
        self.assertEquals(c.containsByAttribute['mob'][0](), m1)
        c.remove(m1)
        self.assertFalse('mob1' in c.containsById)
        self.assertEquals(c.containsByAttribute['mob'][0](), m2)
        c.remove(m2)
        self.assertFalse('mob2' in c.containsById)
        self.assertEquals(c.containsByAttribute['mob'], [])
        pass

if __name__ == "__main__":
    unittest.main()

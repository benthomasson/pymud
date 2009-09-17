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
        o.location = P.null

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
        o.sendMessage("container",contains = self.contains)

    def checkHold(self,o):
        pass

    def checkRemove(self,o):
        pass

class SlottedContainer(Container):

    slotNames = []

    def __init__(self):
        Container.__init__(self)
        self.slots = {}

    def add(self,o,slot=None):
        if not slot:
            Container.add(self,o)
            return
        self.checkHoldSlot(o,slot)
        if slot in self.slots:
            other = self.slots[slot]()
            self.add(other)
        self.slots[slot] = P(o)
        o.location = P(self)
        o.locationSlot = slot

    def remove(self,o):
        if not o.locationSlot:
            Container.remove(self,o)
            return
        if o.locationSlot and o.locationSlot in self.slots:
            del self.slots[o.locationSlot]
        o.location = P.null
        o.locationSlot = None

    def checkHoldSlot(self,o,slot):
        if slot not in self.slotNames:
            raise GameException("You cannot put something there")
        if slot not in o.fitsInSlots:
            raise GameException("It does not fit there")

    def checkRemoveSlot(self,o,slot):
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
        self.assert_(m.location)
        c.remove(m)
        self.assertFalse('mob' in c.contains)
        self.assertFalse(m.location)
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

class TestSlotted(unittest.TestCase):
    
    def testNonSlotted(self):
        from item import Item
        c = SlottedContainer()
        c.id = "container"
        thing = Item(id='thing')
        c.add(thing)
        self.assertEquals(thing.location(),c)
        self.assert_('thing' in c.contains)
        c.remove(thing)
        self.assertFalse(thing.location)
        self.assertFalse('thing' in c.contains)

    def testSlotted(self):
        from item import Item
        c = SlottedContainer()
        c.id = "container"
        c.slotNames = ['hand']
        thing = Item(id='thing')
        thing.fitsInSlots = ['hand']
        c.add(thing,'hand')
        self.assertEquals(c.slots['hand'](),thing)
        self.assertEquals(thing.location(),c)
        self.assertEquals(thing.locationSlot,'hand')
        c.remove(thing)
        self.assertFalse(thing.location)
        self.assertFalse(thing.locationSlot)
        self.assertRaises(GameException,c.add,thing,'head')

    def testMoveSlots(self):
        from item import Item
        c = SlottedContainer()
        c.id = "container"
        c.slotNames = ['head','hand']
        thing = Item(id='thing')
        thing.fitsInSlots = ['hand','head']
        c.add(thing,'hand')
        self.assertEquals(c.slots['hand'](),thing)
        self.assertEquals(thing.location(),c)
        self.assertEquals(thing.locationSlot,'hand')
        c.add(thing,'head')
        self.assertEquals(c.slots['head'](),thing)
        self.assertEquals(thing.location(),c)
        self.assertEquals(thing.locationSlot,'head')

if __name__ == "__main__":
    unittest.main()

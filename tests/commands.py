#!/usr/bin/env python

import unittest
from pymud.testfixture import RoomTestFixture, ZoneTestFixture
from pymud.persist import P
from pymud import builder 
import logging

class TestCommands(RoomTestFixture):

    def setUp(self):
        RoomTestFixture.setUp(self)
        from pymud.mob import Mob
        self.createHere("mob",Mob)

    def testSay(self):
        self.mob.doCommand("say hi")
        self.assertEquals(len(self.messages),2)

    def testSet(self):
        self.mob.doCommand("set a 5")
        self.assertEquals(self.mob.variables['a'],'5')
        self.assertEquals(len(self.messages),1)

    def testLook(self):
        self.mob.doCommand("look")
        self.assertEquals(len(self.messages),1)

    def testLook2(self):
        self.mob.doCommand("look mob")
        self.assertEquals(len(self.messages),1)

    def testHelp(self):
        self.mob.doCommand("help")
        self.assertEquals(len(self.messages),1)

    def testHelp2(self):
        self.mob.doCommand("help commands")
        self.assertEquals(len(self.messages),1)

    def testCommands(self):
        self.mob.doCommand("commands")
        self.assertEquals(len(self.messages),1)

    def testGetDrop(self):
        from pymud.item import Item
        self.createHere('thingy',Item)
        self.assertEquals(self.thingy.location(),self.room)
        self.mob.doCommand("get thing")
        self.mob.doCommand("inventory")
        self.assertEquals(self.thingy.location(),self.mob)
        self.mob.doCommand("drop thing")
        self.assertEquals(self.thingy.location(),self.room)
        self.assertEquals(len(self.messages),3)

    def testGo(self):
        from pymud.room import Room
        self.create('home',Room)
        self.room.addExit('home',self.home)
        self.assertEquals(self.mob.location(),self.room)
        self.mob.doCommand("go home")
        self.assertEquals(self.mob.location(),self.home)

    def testBreak(self):
        self.mob.doCommand("break")
        self.assertEquals(len(self.messages),0)

    def testStop(self):
        self.mob.doCommand("stop")
        self.assertEquals(len(self.messages),0)

    def testDo(self):
        self.mob.doCommand("do hi")
        self.mob.run(0)
        self.assertEquals(len(self.messages),2)

    def testScript(self):
        self.mob.scripts['looptest'] = """\
loop {
say hi
}
"""
        self.mob.doCommand("script")
        self.mob.run(0)
        self.assertEquals(len(self.messages),1)

    def testScript2(self):
        self.mob.scripts['looptest'] = """\
loop {
    say ho
}
"""
        self.mob.doCommand("do looptest")
        self.mob.run(0)
        self.mob.run(0)
        self.mob.run(0)
        self.mob.run(0)
        self.mob.run(0)
        self.assertEquals(len(self.messages),10)

    def testScript3(self):
        self.mob.scripts['looptest'] = """\
loop {
    say ho
    break
}
"""
        self.mob.doCommand("do looptest")
        self.mob.run(0)
        self.mob.run(0)
        self.mob.run(0)
        self.mob.run(0)
        self.mob.run(0)
        self.assertEquals(len(self.messages),2)

    def testScript4(self):
        self.mob.scripts['looptest'] = """\
loop {
    say ho
    stop
}
"""
        self.mob.doCommand("do looptest")
        self.mob.run(0)
        self.mob.run(0)
        self.mob.run(0)
        self.mob.run(0)
        self.mob.run(0)
        self.assertEquals(len(self.messages),2)

    def testWait(self):
        self.mob.doCommand("wait 10")
        for x in xrange(10):
            self.mob.run(x)
        self.assertEquals(len(self.messages),2)

class TestCommands2(ZoneTestFixture):

    def setUp(self):
        ZoneTestFixture.setUp(self)
        from pymud.mob import Mob
        self.mob = builder.create(Mob,'mob',self.room)
        self.mob.addListener(self)

    def testCreate(self):
        self.assert_(self.mob)
        self.assertEquals(self.mob.id,'mob')
        self.assertEquals(self.mob.name,'mob')
        self.assertEquals(self.mob.location(),self.room)
        self.assertEquals(self.room.zone(),self.zone)

    def testMap(self):
        self.mob.doCommand("map")
        self.assertEquals(len(self.messages),1)

    def testGo(self):
        self.assertEquals(self.mob.location(),self.room)
        self.mob.doCommand("go east")
        self.assertEquals(self.mob.location(),self.zone.rooms[2,1,0]())
        self.mob.doCommand("go west")
        self.assertEquals(self.mob.location(),self.room)

    def testTrigger(self):
        self.mob.doCommand("trigger enter map")
        self.assertEquals(self.mob.triggers['enter'],"map")
        self.mob.doCommand("go east")
        self.assertEquals(len(self.messages),3)

    def testTriggerClear(self):
        self.mob.doCommand("trigger enter map")
        self.mob.doCommand("trigger enter clear")
        self.assertFalse('enter' in self.mob.triggers)
        self.mob.doCommand("go east")
        self.assertEquals(len(self.messages),3)

    def testGetAll(self):
        from pymud.item import Item
        self.a = builder.create(Item,None,self.room)
        self.b = builder.create(Item,None,self.room)
        self.c = builder.create(Item,None,self.room)
        self.d = builder.create(Item,None,self.room)
        self.assertEquals(self.a.location(),self.room)
        self.assertEquals(self.b.location(),self.room)
        self.assertEquals(self.c.location(),self.room)
        self.assertEquals(self.d.location(),self.room)
        self.mob.doCommand("get all")
        self.assertEquals(self.a.location(),self.mob)
        self.assertEquals(self.b.location(),self.mob)
        self.assertEquals(self.c.location(),self.mob)
        self.assertEquals(self.d.location(),self.mob)

    def testDropAll(self):
        self.testGetAll()
        self.mob.doCommand("drop all")
        self.assertEquals(self.a.location(),self.room)
        self.assertEquals(self.b.location(),self.room)
        self.assertEquals(self.c.location(),self.room)
        self.assertEquals(self.d.location(),self.room)

    def testDropAllThing(self):
        self.testGetAll()
        self.mob.doCommand("drop all.thing")
        self.assertEquals(self.a.location(),self.room)
        self.assertEquals(self.b.location(),self.room)
        self.assertEquals(self.c.location(),self.room)
        self.assertEquals(self.d.location(),self.room)

    def testLoop(self):
        self.mob.doCommand("""\
loop {
say hi
}
""")
        self.mob.run(0)
        self.mob.run(0)
        self.mob.run(0)
        self.assertEquals(len(self.messages),4)

    def testRandom(self):
        self.mob.doCommand("""\
random {
say hi
say ho
say he
}
""")
        self.mob.run(0)
        self.mob.run(0)
        self.mob.run(0)
        self.assertEquals(len(self.messages),1)
        self.assert_(self.messages[0].dict['message'] in ['hi','ho','he'])



if __name__ == "__main__":
    
    unittest.main()

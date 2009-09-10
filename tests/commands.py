#!/usr/bin/env python

import unittest
from pymud.testfixture import RoomTestFixture

class TestCommands(RoomTestFixture):

    def setUp(self):
        RoomTestFixture.setUp(self)
        from pymud.mob import Mob
        self.mob = self.createHere("mob",Mob)

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

if __name__ == "__main__":
    unittest.main()

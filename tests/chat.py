#!/usr/bin/env python

import unittest
from pymud.testfixture import TestFixture
from pymud.chat import ChatRoom

class TestChat(TestFixture):

    def setUp(self):
        TestFixture.setUp(self)
        self.id = 'test'

    def receiveMessage(self,message):
        print message.type, message.dict

    def test(self):
        chat = self.persist.getOrCreate("globalchat",ChatRoom,name="global")
        chat.addListener(self)
        chat.sendMessage("chat",message="hi",name="ed")
        chat.removeListener(self)

if __name__ == "__main__":
    unittest.main()

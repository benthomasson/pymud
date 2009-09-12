#!/usr/bin/env python

import unittest
from pymud.testfixture import TestFixture
from pymud.chat import ChatRoom

class TestChat(TestFixture):

    def test(self):
        self.attributes = { "name": "TestChat" }
        chat = self.persist.getOrCreate("globalchat",ChatRoom,name="global")
        chat.addListener(self)
        chat.sendMessage("chat",message="hi",name="ed",channel=chat.name)
        chat.removeListener(self)

if __name__ == "__main__":
    unittest.main()

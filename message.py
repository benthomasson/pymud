#!/usr/bin/env python

import unittest

from pymud.persist import P

class Message(object):

    def __init__(self,type,**kwargs):
        self.type = type
        self.dict = kwargs

class Channel(object):
    
    def __init__(self):
        self.listeners = {}

    def addListener(self,listener):
        self.listeners[listener.id] = P(listener)

    def removeListener(self,listener):
        if listener.id in self.listeners:
            del self.listeners[listener.id] 

    def sendMessage(self,type,**kwargs):
        message = Message(type,**kwargs)
        for listener in self.listeners.copy().values():
            if listener(): 
                listener().receiveMessage(message)
            else:
                del self.listeners[listener.id]


class TestMessage(unittest.TestCase):

    def test(self):
        m = Message("say",message="hello",name="Ed",id="1")
        print "%(name)s says '%(message)s'" % m.dict


class TestChannel(unittest.TestCase):

    def receiveMessage(self,message):
        print "%(name)s says '%(message)s'" % message.dict

    def test(self):
        self.id = '1'
        c = Channel()
        c.addListener(self)
        self.assert_(c.listeners['1'])
        self.assertEquals(c.listeners['1'].id,'1')
        self.assertEquals(c.listeners['1'].ref,self)
        self.assertEquals(c.listeners['1']().id,'1')
        self.assertEquals(c.listeners['1'](),self)
        c.sendMessage("say",message="hello",name="Ed",id="1")
        self.deleted = True
        c.sendMessage("say",message="hello",name="Ed",id="1")


if __name__ == "__main__":
    unittest.main()


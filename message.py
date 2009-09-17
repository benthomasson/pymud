#!/usr/bin/env python

import unittest

from pymud.persist import P
from pymud.container import Container

class Message(object):

    def __init__(self,type,**kwargs):
        self.type = type
        self.dict = {'_exclude':[]}
        self.dict.update(kwargs)

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
        self._sendMessage(message)

    def _sendMessage(self,message):
        _exclude = message.dict['_exclude']
        for listener in self.listeners.copy().values():
            if listener() and listener() not in _exclude:
                listener().receiveMessage(message)
            elif not listener():
                del self.listeners[listener.id]

class ContainerChannel(Channel,Container):
    
    def __init__(self):
        Container.__init__(self)

    def addListener(self,listener):
        Container.add(self,listener)

    def removeListener(self,listener):
        Container.remove(self,listener)

    def _sendMessage(self,message):
        _exclude = message.dict['_exclude']
        for listener in self.contains.copy().values():
            if listener() and listener() not in _exclude:
                listener().receiveMessage(message)
            elif not listener():
                del self.contains[listener.id]

class RepeaterMixin(object):

    def receiveMessage(self,message):
        self._sendMessage(message)


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
        c.sendMessage("say",message="hello1",name="Ed",id="1")
        c.sendMessage("say",message="hello3",name="Ed",id="1",_exclude=[self])
        self.deleted = True
        c.sendMessage("say",message="hello2",name="Ed",id="1")


if __name__ == "__main__":
    unittest.main()


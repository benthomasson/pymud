

from pymud.persist import Persistent
from pymud.message import Channel


class ChatRoom(Channel,Persistent):

    def __init__(self,name,id):
        Channel.__init__(self)
        Persistent.__init__(self)
        self.id = id
        self.name = name

    def addListener(self,listener):
        Channel.addListener(self,listener)
        self.sendMessage("chatjoin",name=listener.attributes['name'],channel=self.name)

    def removeListener(self,listener):
        self.sendMessage("chatleave",name=listener.attributes['name'],channel=self.name)
        Channel.removeListener(self,listener)

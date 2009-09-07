
from pymud.message import Channel
from pymud.container import Container
from pymud.sim import Sim

class Room(Sim, Channel, Container):

    description = "a plain room"
    detail = "a very plain room"
    attributes = {'name':'room'}

    def __init__(self,id=None):
        Sim.__init__(self)
        Channel.__init__(self)
        Container.__init__(self)
        self.id = id
        self.exits = {}

    def add(self,o):
        self.addListener(o)
        Container.add(self,o)

    def remove(self,o):
        self.removeListener(o)
        Container.remove(self,o)

    def __setstate__(self,state):
        self.__dict__ = state.copy()
        if not hasattr(self,'exits'): self.exits = {}
        if not hasattr(self,'scripts'): self.scripts = {}

    def seen(self,o):
        o.sendMessage("look",description=self.description)
        Container.seen(self,o)
        if self.exits:
            o.sendMessage("header",title="Exits")
            for name,exit in self.exits.copy().iteritems():
                if exit():
                    o.sendMessage("exit",name=name)
                else:
                    del self.exits[name]




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

    def add(self,o):
        self.addListener(o)
        Container.add(self,o)

    def remove(self,o):
        self.removeListener(o)
        Container.remove(self,o)

    def seen(self,o):
        o.sendMessage("look",description=self.description)
        Container.seen(self,o)


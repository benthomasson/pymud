

from pymud.message import Channel
from pymud.container import Container
from pymud.persist import Persistent

class Room(Persistent, Channel, Container):

    description = "a plain room"
    detail = "a very plain room"

    def __init__(self,id=None):
        Persistent.__init__(self)
        Channel.__init__(self)
        Container.__init__(self)
        self.id = id

    def seen(self,o):
        o.sendMessage("look",description=self.description)
        Container.seen(self,o)

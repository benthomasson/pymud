

from pymud.message import Channel
from pymud.container import Container
from pymud.persist import Persistent

class Room(Persistent, Channel, Container):

    def __init__(self):
        Persistent.__init__(self)
        Channel.__init__(self)
        Container.__init__(self)



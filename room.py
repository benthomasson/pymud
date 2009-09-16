
from pymud.message import ContainerChannel, Container
from pymud.sim import Sim
from pymud.persist import P

class Room(Sim, ContainerChannel):

    description = "a plain room"
    detail = "a very plain room"
    attributes = []
    name = 'room'
    mapCharacter = ' '
    mapColor = ""
    zone = P.null

    def __init__(self,id=None):
        Sim.__init__(self)
        ContainerChannel.__init__(self)
        self.id = id
        self.exits = {}

    def checkEnter(self,o):
        pass

    def checkLeave(self,o):
        pass

    def enter(self,o):
        self.checkEnter(o)
        if o.location() and isinstance(o.location(),Room):
            o.location().leave(o)
        self.addListener(o)

    def leave(self,o):
        self.checkLeave(o)
        self.removeListener(o)

    def add(self,o):
        self.addListener(o)

    def remove(self,o):
        self.removeListener(o)

    def __setstate__(self,state):
        self.__dict__ = state.copy()

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

class Zone(Sim,ContainerChannel):

    description = "a plain zone"
    detail = "a very plain zone"
    attributes = []
    name = 'zone'
    mapDistance = 10

    def __init__(self,id=None):
        Sim.__init__(self)
        ContainerChannel.__init__(self)
        self.id = id
        self.rooms = {}
        self.coordinates = {}


    def add(self,o,x,y,z=0):
        self.coordinates[o.id] = (x,y,z)
        self.rooms[(x,y,z)] = P(o)
        self.addListener(o)
        o.zone = P(self)

    def remove(self,o):
        if o.id in self.coordinates:
            (x,y,z) = self.coordinates[o.id]
            del self.coordinates[o.id]
            if (x,y,z) in self.rooms:
                del self.rooms[(x,y,z)]
        self.removeListener(o)
        o.zone = self

    def showMap(self,observer,location):
        observer.sendMessage("map",location=location,zone=self)


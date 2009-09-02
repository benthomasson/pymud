
from mob import Mob
from room import Room
from pymud.chainedmap import ChainedMap
from pymud.persist import P
from pymud.scheduler import Scheduler
from pymud.exceptions import *
import sys
import traceback

def create(self,klass,id=None):
    """Create an instance of a class"""
    klasses = {"Mob":Mob, "Room":Room}
    m = klasses[klass](id=id)
    P.persist.persist(m)
    Scheduler.scheduler.schedule(m)
    self.sendMessage("created",id=m.id,klass=klass,name=self.id)

def createHere(self,klass,id=None):
    """Create an instance of a class in this room"""
    klasses = {"Mob":Mob, "Room":Room}
    m = klasses[klass](id=id)
    P.persist.persist(m)
    Scheduler.scheduler.schedule(m)
    if self.location():
        self.location().add(m)
    self.sendMessage("created",id=m.id,klass=klass,name=self.id)

def goto(self,id):
    """Go to another room by id"""
    newLocation = P.persist.get(id)
    self.sendMessage("action",description="leave %s" % self.location().__class__.__name__)
    newLocation.add(self)
    self.sendMessage("action",description="arrive at %s" % self.location().__class__.__name__)

def shutdown(self):
    """Shutdown the server"""
    self.sendMessage("say",message="shutdown!",name=self.id)
    raise ShutdownSignal("shutdown!")

class Creator(Mob):

    commands = ChainedMap(  parent=Mob.commands,
                            map={   "create":create,
                                    "goto":goto,
                                    "createhere":createHere,
                                    "shutdown":shutdown, })

    description = "something strange, like a bunch of green glowing letters"

    def __init__(self,*args,**kwargs):
        Mob.__init__(self,*args,**kwargs)
        self.commands = ChainedMap(parent=Creator.commands)




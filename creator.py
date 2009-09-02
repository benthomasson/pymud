
from mob import Mob
from room import Room
from pymud.chainedmap import ChainedMap
from pymud.persist import P
from pymud.scheduler import Scheduler
from pymud.exceptions import *
import sys
import traceback

def create(self,klass):
    klasses = {"Mob":Mob, "Room":Room}
    m = klasses[klass]()
    P.persist.persist(m)
    Scheduler.scheduler.schedule(m)
    self.sendMessage("created",id=m.id,klass=klass,name=self.id)

def goto(self,id):
    newLocation = P.persist.get(id)
    self.sendMessage("action",description="leave %s" % self.location().__class__.__name__)
    newLocation.add(self)
    self.sendMessage("action",description="arrive at %s" % self.location().__class__.__name__)

def shutdown(self):
    self.sendMessage("say",message="shutdown!",name=self.id)
    raise ShutdownSignal("shutdown!")

class Creator(Mob):

    commands = ChainedMap(  parent=Mob.commands,
                            map={   "create":create,
                                    "goto":goto,
                                    "shutdown":shutdown, })

    def __init__(self,*args,**kwargs):
        Mob.__init__(self,*args,**kwargs)
        self.commands = ChainedMap(parent=Creator.commands)




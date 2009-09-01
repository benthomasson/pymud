
from mob import Mob
from pymud.chainedmap import ChainedMap
from pymud.persist import P
from pymud.scheduler import Scheduler
from pymud.message import Message
from pymud.exceptions import *

def create(self,klass):
    klasses = {"Mob":Mob}
    m = klasses[klass]()
    P.persist.persist(m)
    Scheduler.scheduler.schedule(m)
    self.sendMessage(Message("created",id=m.id,klass=klass,name=self.id))

def shutdown(self):
    self.sendMessage(Message("say",message="shutdown!",name=self.id))
    raise ShutdownSignal("shutdown!")

class Creator(Mob):

    commands = ChainedMap(  parent=Mob.commands,
                            map={   "create":create,
                                    "shutdown":shutdown})



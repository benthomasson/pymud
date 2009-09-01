
from mob import Mob
from pymud.chainedmap import ChainedMap
from pymud.persist import P
from pymud.scheduler import Scheduler
from pymud.message import Message

def create(self,klass):
    klasses = {"Mob":Mob}
    m = klasses[klass]()
    P.persist.persist(m)
    self.sendMessage(Message("created",id=m.id,klass=klass,name=self.id))

class Creator(Mob):

    commands = ChainedMap(parent=Mob.commands,map={"create":create})



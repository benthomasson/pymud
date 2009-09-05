
from pymud.sim import Sim
from pymud.mob import Mob
from pymud.room import Room
from pymud.chainedmap import ChainedMap
from pymud.persist import P
from pymud.scheduler import Scheduler
from pymud.mobmarket import MobMarket
from pymud.exceptions import *
import sys
import traceback

def getAllSubclasses(klass):
    klasses = []
    klasses += klass.__subclasses__()
    for x in klass.__subclasses__():
        klasses += getAllSubclasses(x)
    return list(set(klasses))

def create(self,klass,id=None):
    """Create an instance of a class"""
    klasses = dict(map(lambda x:(x.__name__,x),getAllSubclasses(Sim)))
    m = klasses[klass](id=id)
    P.persist.persist(m)
    if isinstance(m,Mob):
        MobMarket.market.add(m)
    Scheduler.scheduler.schedule(m)
    self.sendMessage("created",id=m.id,klass=klass,article=klasses[klass].article,name=self.id)
    return m

def createhelper(self,current,full):
    klasses = map(lambda x:x.__name__,getAllSubclasses(Sim))
    return filter(lambda x:x.startswith(current),klasses)

create.tabcomplete = createhelper

def createHere(self,klass,id=None):
    """Create an instance of a class in this room"""
    m = create(self,klass,id)
    if self.location():
        self.location().add(m)

createHere.tabcomplete = createhelper

def goto(self,id):
    """Go to another room by id"""
    newLocation = P.persist.get(id)
    self.sendMessage("action",description="leave %s" % self.location().__class__.__name__)
    newLocation.add(self)
    self.sendMessage("action",description="arrive at %s" % self.location().__class__.__name__)

def gotohelper(self,current,full):
    rooms = []
    for x in P.persist.db.cache.values():
        if isinstance(x,Room):
            rooms.append(x.id)
    return filter(lambda x:x.startswith(current),rooms)


goto.tabcomplete = gotohelper

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
    detail = "what appears to be an infinite string of numbers"
    attributes = {'name':'Creator'}

    def __init__(self,*args,**kwargs):
        Mob.__init__(self,*args,**kwargs)
        self.commands = ChainedMap(parent=Creator.commands)




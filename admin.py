"""Admin commands"""

from pymud.sim import Sim
from pymud.mob import Mob
from pymud.room import Room
from pymud.persist import P
from pymud.scheduler import Scheduler
from pymud.mobmarket import MobMarket

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

def addexit(self,name,to):
    to = P.persist.get(to)
    self.location().exits[name] = P(to)

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


def spy(self,target=None):
    if not target:
        target = self
    elif target == "here":
        target = self.location()
    elif self.location():
        target = self.location().get(attribute=target)()
    print target.__class__
    for name,value in target.__dict__.iteritems():
        print name,value

def kill(self,target=None):
    if not target:
        return
    if not self.location():
        return
    target = self.location().get(attribute=target)
    id = target.id
    target().sendMessage("notice",notice="You have been killed by the cruel hand of fate")
    target.delete()
    self.sendMessage("notice",notice="You killed %s" % id)



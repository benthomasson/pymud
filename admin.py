"""Admin commands"""

from pymud.sim import Sim
from pymud.mob import Mob
from pymud.room import Room
from pymud.persist import P
from pymud.scheduler import Scheduler
from pymud.mobmarket import MobMarket
from pymud.exceptions import *
from pymud import builder 

def getAllSubclasses(klass):
    klasses = []
    klasses += klass.__subclasses__()
    for x in klass.__subclasses__():
        klasses += getAllSubclasses(x)
    return list(set(klasses))

def load(self,moduleName):
    exec "import %s" % moduleName
    module = eval(moduleName)
    self.sendMessage("notice",notice="Loaded %s" % moduleName)

def create(self,klass,id=None):
    """\
    Create an instance of a class.

    create <class> <id>

    """
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
    """\
    Create an instance of a class in this room.

    createhere <class> <id>
    """
    m = create(self,klass,id)
    if self.location():
        self.location().add(m)

createHere.tabcomplete = createhelper

def addexit(self,name,to):
    """\
    Add an exit from the current room to another.
    addexit <name> <to-id>
    """
    to = P.persist.get(to)
    self.location().exits[name] = P(to)

def add2dzone(self,width,breadth,klass):
    width = int(width)
    breadth = int(breadth)
    klasses = dict(map(lambda x:(x.__name__,x),getAllSubclasses(Room)))
    start = builder.add2dZone(width,breadth,klasses[klass])
    self.sendMessage("created",id=start.id,klass=klass,article=klasses[klass].article,name=self.id)


def goto(self,id):
    """\
    Go to another room by id.

    goto <id>
    """
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
    """\
    Shutdown the server.

    shutdown
    """
    self.sendMessage("say",message="shutdown!",name=self.id)
    raise ShutdownSignal("shutdown!")


def spy(self,target=None):
    """\
    Inspect the variables on an item or mob.

    spy <target>
    """
    if not target:
        target = self
    elif target == "here":
        target = self.location()
    elif self.location():
        target = self.location().get(attribute=target)()
    print target.__class__
    for name,value in target.__dict__.iteritems():
        print name,value

def spyp(self,id):
    """\
    Inspect the variables on an item or mob by id.

    spyp <id>
    """
    target = P.persist.get(id)
    for name,value in target.__dict__.iteritems():
        print name,value

def kill(self,target=None):
    """\
    Instantly and painlessly kill a mob.

    kill <target>
    """
    if not target:
        return
    if not self.location():
        return
    target = self.location().get(attribute=target)
    id = target.id
    target().sendMessage("notice",notice="You have been killed by the cruel hand of fate")
    target.delete()
    self.sendMessage("notice",notice="You killed %s" % id)


def mutate(self,target,klass):

    if target == "here":
        target = self.location()
    else:
        target = self.location().get(attribute=target)()
    klasses = dict(map(lambda x:(x.__name__,x),getAllSubclasses(Sim)))
    oldname = target.name
    target.__class__ = klasses[klass]
    target.mutate()
    self.sendMessage("notice",notice="%s mutated into a %s" % (oldname,target.name))
    


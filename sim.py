
from pymud.persist import Persistent, P
from pymud.exceptions import *
from pymud.chainedmap import ChainedMap
from pymud.scheduler import Scheduler
from pymud.rule import runRules

class Sim(Persistent):

    description = "something"
    detail = "maybe it's nothing"
    article = "a"
    attributes = []
    ticksPerTurn = 0
    name = 'thing'
    location = P.null
    locationSlot = None
    fitsInSlots = []
    commands = {}
    rules = []

    def __init__(self):
        Persistent.__init__(self)

    def __repr__(self):
        return "<" + self.__class__.__name__ +  ":" + self.id + ">"

    def checkGet(self,getter):
        raise GameException("You cannot lift it.")

    def checkDrop(self,getter):
        raise GameException("It's too sticky.")

    def checkUse(self,getter):
        raise GameException("%s does not look usable" % self.name)

    def run(self,*ignore):
        pass

    def update(self,tick):
        self.lastUpdate = tick
        self.runRules()

    def runRules(self):
        runRules(self,self.rules)

    def reschedule(self):
        Scheduler.scheduler.schedule(self)

    def delete(self):
        P.persist.delete(self)

    def sendLocationMessage(self,*args,**kwargs):
        if self.location():
            self.location().sendMessage(*args,**kwargs)

    def sendMessage(self,*ignore,**kwignore):
        pass




from pymud.persist import P
from pymud.scheduler import Scheduler
from pymud.mobmarket import MobMarket
from pymud.mob import Mob

def create(klass,id=None,location=None):
    o = klass(id=id)
    P.persist.persist(o)
    if isinstance(o,Mob):
        MobMarket.market.add(o)
    Scheduler.scheduler.schedule(o)
    if location:
        location.add(o)
    return o

def getOrCreate(klass,id=None,location=None):
    o = P.persist.getOrCreate(id,klass)
    if isinstance(o,Mob):
        MobMarket.market.add(o)
    Scheduler.scheduler.schedule(o)
    if location:
        location.add(o)
    return o

def addExit(room,exit,to):
    room.exits[exit] = P(to)



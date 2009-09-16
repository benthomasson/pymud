
from pymud.persist import P
from pymud.scheduler import Scheduler
from pymud.mobmarket import MobMarket
from pymud.mob import Mob
from pymud.room import Zone

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


def add2dZone(width,breadth,klass):
    zone = create(Zone)
    rooms = {}
    for y in xrange(breadth):
        for x in xrange(width):
            rooms[(x,y)] = create(klass)
            zone.add(rooms[(x,y)],x,y)
    for y in xrange(breadth):
        for x in xrange(width):
            room = rooms[(x,y)]
            if (x-1,y) in rooms:
                addExit(room,'west',rooms[(x-1,y)])
            if (x+1,y) in rooms:
                addExit(room,'east',rooms[(x+1,y)])
            if (x,y-1) in rooms:
                addExit(room,'north',rooms[(x,y-1)])
            if (x,y+1) in rooms:
                addExit(room,'south',rooms[(x,y+1)])
    return rooms[(0,0)] 


    

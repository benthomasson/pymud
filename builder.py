
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

def add2dZone(width,breadth,klass):
    zone = create(Zone)
    rooms = {}
    for y in xrange(breadth):
        for x in xrange(width):
            rooms[(x,y)] = create(klass)
            zone.add(rooms[(x,y)],x,y)
    connectRooms(zone,width,breadth)
    return rooms[(0,0)] 


def connectRooms(zone,width,breadth,depth=0):
    rooms = zone.rooms
    for y in xrange(breadth):
        for x in xrange(width):
            if (x,y,depth) in rooms:
                room = rooms[(x,y,depth)]()
                if (x-1,y,depth) in rooms:
                    room.addExit('west',rooms[(x-1,y,depth)])
                if (x+1,y,depth) in rooms:
                    room.addExit('east',rooms[(x+1,y,depth)])
                if (x,y-1,depth) in rooms:
                    room.addExit('north',rooms[(x,y-1,depth)])
                if (x,y+1,depth) in rooms:
                    room.addExit('south',rooms[(x,y+1,depth)])

def addZoneFromMapFile(id,mapFile,klasses):
    with open(mapFile) as f:
        return addZoneFromMap(id,f.read(),klasses)

def addZoneFromMap(id,zoneMap,klasses):
    if P.persist.exists(id):
        return P.persist.get(id).home
    zone = create(Zone,id)
    lines = zoneMap.splitlines()
    rooms = []
    width = 0
    breadth = 0
    for y,line in zip(xrange(len(lines)),lines):
        if y > breadth:
            breadth = y
        for x,char in zip(xrange(len(line)),line):
            if x > width:
                width = x
            if char in klasses:
                room = create(klasses[char])
                zone.add(room,x,y)
                rooms.append(room)
    connectRooms(zone,width+1,breadth+1)
    if rooms:
        zone.home = rooms[0]
        return rooms[0]
    else:
        return None



    



from pymud.persist import P,Persistent

class MobMarket(Persistent):

    market = None

    def __init__(self,id = None):
        Persistent.__init__(self)
        self.mobs = {}
        self.id = id

    def add(self,mob):
        self.mobs[mob.id] = P(mob)
        
    def remove(self,mob):
        if mob.id in self.mobs:
            del self.mobs[mob.id]

    def getNext(self):
        if self.mobs:
            return self.mobs.popitem()[1]
        else:
            return P.null


from pymud.persist import P

class Container(object):

    def __init__(self):
        self.contains = {}

    def remove(self,o):
        if o.id in self.contains:
            del self.contains[o.id]

    def add(self,o):
        if o.location():
            o.location().remove(o)
        o.location = P(self)
        self.contains[o.id] = P(o)

    def seen(self,o):
        for x in self.contains.values():
            if x():
                o.sendMessage("look",description=x().description)



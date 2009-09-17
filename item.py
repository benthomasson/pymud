
from pymud.sim import Sim
from pymud.persist import P
from pymud.exceptions import *

class Item(Sim):

    location = P.null
    description = "a thing"
    detail = "it's nondescript"
    article = "an"
    
    def __init__(self,id=None):
        Sim.__init__(self)
        self.id = id


    def seen(self,o):
        o.sendMessage("look",description=self.detail)

    def receiveMessage(self,message):
        pass

    def checkGet(self,getter):
        pass

    def checkDrop(self,getter):
        pass

    def checkUse(self,getter):
        pass

    def __call__(self,*ignore,**ignorekw):
        raise GameException("%s is not usable" % self.name)


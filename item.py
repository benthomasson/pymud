
from pymud.sim import Sim
from persist import P

class Item(Sim):

    location = P()
    description = "a thing"
    detail = "it's nondescript"
    article = "an"
    
    def __init__(self,id=None):
        Sim.__init__(self)
        self.id = id



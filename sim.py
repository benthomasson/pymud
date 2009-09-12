
from pymud.persist import Persistent
from pymud.exceptions import *
from pymud.chainedmap import ChainedMap

class Sim(Persistent):

    description = "something"
    detail = "maybe it's nothing"
    article = "a"
    attributes = {'name':'thing'}

    def __init__(self):
        Persistent.__init__(self)

    def __repr__(self):
        return "<" + self.__class__.__name__ +  ":" + self.id + ">"

    def checkGet(self,getter):
        raise GameException("You cannot lift it.")

    def checkDrop(self,getter):
        raise GameException("It's too sticky.")

    def run(self,*ignore):
        pass


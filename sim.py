
from pymud.persist import Persistent

class Sim(Persistent):

    description = "something"
    detail = "maybe it's nothing"
    article = "a"
    attributes = {'name':'thing'}

    def __init__(self):
        Persistent.__init__(self)

    def __repr__(self):
        return "<" + self.__class__.__name__ +  ":" + self.id + ">"

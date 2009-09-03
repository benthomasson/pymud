
from pymud.persist import Persistent

class Sim(Persistent):

    description = "something"
    detail = "maybe it's nothing"
    article = "a"

    def __init__(self):
        Persistent.__init__(self)


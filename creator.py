
from pymud.mob import Mob
from pymud.chainedmap import ChainedMap
from admin import *

class Creator(Mob):

    commands = ChainedMap(  parent=Mob.commands,
                            map={   "create":create,
                                    "add2dzone":add2dzone,
                                    "goto":goto,
                                    "mutate":mutate,
                                    "load":load,
                                    "spy":spy,
                                    "spyp":spyp,
                                    "kill":kill,
                                    "addexit":addexit,
                                    "createhere":createHere,
                                    "shutdown":shutdown,
                                    "EOF":shutdown,
                                    "quit":shutdown,
                                    })

    description = "something strange, like a bunch of green glowing letters"
    detail = "what appears to be an infinite string of numbers"
    attributes = ['creator','Creator']
    name = 'Creator'
    slotNames = ['head','hand']

    def __init__(self,*args,**kwargs):
        Mob.__init__(self,*args,**kwargs)




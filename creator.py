
from pymud.sim import Sim
from pymud.mob import Mob
from pymud.room import Room
from pymud.chainedmap import ChainedMap
from pymud.persist import P
from pymud.scheduler import Scheduler
from pymud.mobmarket import MobMarket
from pymud.exceptions import *
import sys
import traceback
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
    attributes = []
    name = 'Creator'
    slotNames = ['head']

    def __init__(self,*args,**kwargs):
        Mob.__init__(self,*args,**kwargs)
        self.commands = ChainedMap(parent=Creator.commands)




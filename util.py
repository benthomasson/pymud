from pymud.exceptions import *

from pymud.persist import P
from pymud.scheduler import Scheduler

def classname(obj):
    return obj.__class__.__name__

def getAllSubclasses(klass):
    klasses = []
    klasses += klass.__subclasses__()
    for x in klass.__subclasses__():
        klasses += getAllSubclasses(x)
    return list(set(klasses))

def checkVoid(self,message):
    if not self.location():
        raise GameException("You are in the void. %s" % message)

def getFirstTarget(self,target,exception):
    target = self.location().get(attribute=target)
    if target:
        return target[0]
    raise GameException(exception)

def createInstance(klass):
    i = klass()
    P.persist.persist(i)
    Scheduler.scheduler.schedule(i)
    return i




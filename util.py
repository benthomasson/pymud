from pymud.exceptions import *

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
    print target
    target = self.location().get(attribute=target)
    print target
    if target:
        return target[0]
    raise GameException(exception)



import traceback
from pymud.chainedmap import ChainedMap
from pymud.exceptions import *
from pymud.coroutine import step
from pymud.interpreter import interpret

class Scriptable():

    def __init__(self):
        self.commandQueue = []
        self.commandScript = None
        self.backgroundScript = None
        self.variables = {}
        self.commands = ChainedMap(self.__class__.commands)
        self.scripts = ChainedMap(self.__class__.scripts)
        self.triggers = ChainedMap(self.__class__.scripts)

    def run(self,n=1):
        for x in xrange(n):
            try:
                if not self.commandScript and len(self.commandQueue):
                    self.commandScript = interpret(self.commandQueue.pop(0),self)
                if self.commandScript:
                    if not step(self.commandScript):
                        self.commandScript = None
                elif self.backgroundScript:
                    if not step(self.backgroundScript):
                        self.backgroundScript = None
            except GameException, e:
                self.sendMessage("exception",error=str(e))
            except Exception, e:
                message = " ".join(traceback.format_exception(*sys.exc_info()))
                self.sendMessage("error",error=message)

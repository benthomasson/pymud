
import sys,traceback
from pymud.chainedmap import ChainedMap
from pymud.exceptions import *
from pymud.coroutine import step
from pymud.interpreter import interpret

class Scriptable():

    def __init__(self):
        self.commandQueue = []
        self.scriptsQueue = []
        self.commandScript = None
        self.variables = {}
        self.commands = ChainedMap(self.__class__.commands)
        self.scripts = ChainedMap(self.__class__.scripts)
        self.triggers = ChainedMap(self.__class__.triggers)
        self.conditions = ChainedMap(self.__class__.conditions)
        self.waiting = None

    def receiveMessage(self,message):
        if message.type.startswith("_"): return
        self.runTriggerScript(message.type,**message.dict)

    def runTriggerScript(self,type,**kwargs):
        if type in self.triggers:
            script = self.triggers[type]
            if script in self.scripts:
                for name,value in kwargs.iteritems():
                    if name.startswith("_"): continue
                    self.variables["t:" + name] = value
                self.scriptsQueue.append(interpret(self.scripts[script],self))

    def run(self,tick):
        self.update(tick)
        try:
            while len(self.commandQueue) > 0:
                command = interpret(self.commandQueue.pop(0),self)
                if step(command):
                    self.scriptsQueue.append(command)
            if not self.commandScript and len(self.scriptsQueue):
                self.commandScript = self.scriptsQueue.pop(0)
            if self.commandScript:
                if not step(self.commandScript):
                    self.commandScript = None
        except GameException, e:
            self.sendMessage("exception",error=str(e))
        except Exception, e:
            #message = " ".join(traceback.format_exception(*sys.exc_info()))
            self.sendMessage("error",error=str(e))

    def doCommand(self,command):
        self.commandQueue.append(command+"\n")
        self.run(0)


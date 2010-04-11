
import sys,traceback
from pymud.chainedmap import ChainedMap, MultipleMap
from pymud.exceptions import *
from pymud.coroutine import step
from pymud.interpreter import interpret

import logging

errorLogger = logging.getLogger("pymud.error")

class Updatable(object):

    def run(self,tick):
        self.update(tick)

class Scriptable(Updatable):

    def __init__(self):
        self.commandQueue = []
        self.scriptsQueue = []
        self.commandScript = None
        self.variables = {}
        self.commands = MultipleMap(self.__class__.commands,mapsFunc=self.getOtherCommands)
        self.scripts = ChainedMap(self.__class__.scripts)
        self.triggers = ChainedMap(self.__class__.triggers)
        self.conditions = ChainedMap(self.__class__.conditions)
        self.waiting = None

    def getOtherCommands(self):
        return []

    def receiveMessage(self,message):
        if message.type.startswith("_"): return
        self.runTrigger(message.type,**message.dict)

    def runTrigger(self,event,**kwargs):
        if event in self.triggers:
            for name,value in kwargs.iteritems():
                if name.startswith("_"): continue
                self.variables["t:" + name] = value
            script = self.triggers[event]
            if script.strip():
                self.commandQueue.append(script + "\n")
                return True
        return False

    def run(self,tick):
        Updatable.run(self,tick)
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
        except BreakException:
            pass
        except GameException, e:
            self.sendMessage("exception",error=str(e))
            self.runTrigger("failure")
        except Exception, e:
            self.sendMessage("error",error=str(e))
            message = " ".join(traceback.format_exception(*sys.exc_info()))
            errorLogger.error("""\
--------------------------------------------------------------------------------
%s 
%s
--------------------------------------------------------------------------------
""" % (self.name,message))
            if not self.runTrigger("error"):
                self.runTrigger("failure")

    def appendCommand(self,command):
        self.commandQueue.append(command+"\n")

    def doCommand(self,command):
        self.appendCommand(command)
        self.run(0)



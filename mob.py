#!/usr/bin/env python

import sys
import traceback
import unittest
import pickle
from pymud.chainedmap import ChainedMap
from pymud.coroutine import step
from pymud.interpreter import interpret
from pymud.message import Channel,RepeaterMixin
from pymud.formatter import ColorTextFormatter
from pymud.container import Container
from pymud.sim import Sim
from pymud.persist import P
from pymud.exceptions import *
from commands import *

class Mob(RepeaterMixin,Channel,Container,Sim):

    commands = ChainedMap(map={ 'say':say,
                                'look': look,
                                'help': help,
                                'do': do,
                                'go': go,
                                'script': script,
                                'get': get,
                                'drop': drop,
                                'inventory': inventory,
                                'quit': quit,
                                'set':setVariable})
    location = P.null
    description = "an ugly son of a mob"
    detail = "a really ugly son of a mob"
    attributes = {'name':'mob'}
    interface = None

    def __init__(   self,
                    variables=None,
                    commands=None,
                    id=None):
        Channel.__init__(self)
        Container.__init__(self)
        Sim.__init__(self)
        self.id = id
        self.deleted = False
        self.commandScript = None
        self.backgroundScript = None
        self.commandQueue = []
        self.location = P.null
        self.interface = None
        if variables:
            self.variables = variables
        else:
            self.variables = {}
        if commands:
            self.commands = commands
        else:
            self.commands = ChainedMap(Mob.commands)

    def default(self,args):
        say(*[self] + args)

    def __setstate__(self,state):
        self.__dict__ = state.copy()
        self.commands.parent = self.__class__.commands
        self.commandScript = None
        self.interface = None
        if not hasattr(self,"scripts"): self.scripts = {}

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['commandScript']
        del state['interface']
        return state

    def applyCommand(self,command,arguments=[]):
        func = self.commands[command]
        if hasattr(func,'im_self') and func.im_self:
            func(*arguments)
        else:
            func(*[self] + arguments)

    def seen(self,o):
        o.sendMessage("look",description=self.detail)

    def run(self,n=1):
        #print 'run %s' % self.id
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

class Test(unittest.TestCase, ColorTextFormatter):

    def setUp(self):
        self.id = None

    def receiveMessage(self,message):
        sys.stdout.write("\n")
        sys.stdout.write(self.formatMessage(message))
        sys.stdout.write("\n")
        sys.stdout.flush()

    def testSayHi(self):
        from pymud.persist import P
        amob = Mob()
        amob.addListener(P(self))
        say(amob,"hi")
        amob.applyCommand("say",["hi"])

    def testSet(self):
        amob = Mob()
        setVariable(amob,'a','5')
        self.assertEquals(amob.variables['a'],'5')
        del amob.variables['a']
        amob.applyCommand("set",["a","5"])
        self.assertEquals(amob.variables['a'],'5')

    def testPickleEmpty(self):
        mob1 = Mob()
        out = pickle.dumps(mob1,pickle.HIGHEST_PROTOCOL)
        mob2 = pickle.loads(out)
        self.assertNotEquals(mob1,mob2)

    def testPickleVariables(self):
        from pymud.persist import P
        mob1 = Mob()
        mob1.addListener(P(self))
        setVariable(mob1,'a','5')
        say(mob1,'hi1')
        self.assertEquals(mob1.variables['a'],'5')
        out = pickle.dumps(mob1,pickle.HIGHEST_PROTOCOL)
        mob2 = pickle.loads(out)
        mob2.addListener(P(self))
        self.assertEquals(mob2.variables['a'],'5')
        say(mob2,'hi2')

    def testPickleCommands(self):
        from pymud.persist import P
        mob1 = Mob()
        mob1.addListener(P(self))
        mob1.commands['uber'] = uber
        mob1.applyCommand('say',['hi'])
        mob1.applyCommand('uber')
        out = pickle.dumps(mob1,pickle.HIGHEST_PROTOCOL)
        #print out
        mob2 = pickle.loads(out)
        mob2.addListener(P(self))
        mob2.applyCommand('say',['hi'])
        mob2.applyCommand('uber')

    def testRunEmpty(self):
        amob = Mob()
        amob.run()

    def testRun(self):
        from pymud.persist import P
        amob = Mob()
        amob.addListener(P(self))
        amob.commandQueue.append("say hi\n")
        amob.commandQueue.append("say hi\n")
        amob.commandQueue.append("say hi\n")
        self.assertFalse(amob.commandScript)
        self.assertEquals(len(amob.commandQueue),3)
        amob.run()
        self.assertEquals(len(amob.commandQueue),2)
        self.assertFalse(amob.commandScript)
        amob.run()
        self.assertEquals(len(amob.commandQueue),1)
        self.assertFalse(amob.commandScript)
        amob.run()
        self.assertEquals(len(amob.commandQueue),0)
        self.assertFalse(amob.commandScript)
        amob.run()
        self.assertEquals(len(amob.commandQueue),0)
        self.assertFalse(amob.commandScript)

if __name__ == "__main__":
    unittest.main()

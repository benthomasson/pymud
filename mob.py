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
from pymud.scriptable import Scriptable
from pymud.persist import P
from pymud.exceptions import *
from commands import *

class Mob(RepeaterMixin,Channel,Container,Scriptable,Sim):

    commands = ChainedMap(map={ 'say':say,
                                'look': look,
                                'chat': chat,
                                'help': help,
                                'commands': commands,
                                'do': do,
                                'go': go,
                                'script': script,
                                'trigger': trigger,
                                'get': get,
                                'drop': drop,
                                'inventory': inventory,
                                'quit': quit,
                                'description': description,
                                'break': breakCommand,
                                'wait': wait,
                                'stop': stop,
                                'set':setVariable})
    scripts = ChainedMap(map={'hi':'say hi\n'})
    triggers = ChainedMap()
    conditions = ChainedMap(map={'alive':True})
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
        Scriptable.__init__(self)
        Sim.__init__(self)
        self.id = id
        self.location = P.null
        self.interface = None
        if variables:
            self.variables = variables
        if commands:
            self.commands = commands

    def default(self,args):
        say(*[self] + args)

    def __setstate__(self,state):
        self.__dict__ = state.copy()
        self.commands.parent = self.__class__.commands
        self.scripts.parent = self.__class__.scripts
        self.triggers.parent = self.__class__.triggers
        self.conditions.parent = self.__class__.conditions
        self.commandScript = None
        self.scriptsQueue = []
        self.interface = None

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['commandScript']
        del state['scriptsQueue']
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

    def receiveMessage(self,message):
        RepeaterMixin.receiveMessage(self,message)
        Scriptable.receiveMessage(self,message)

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
        self.assertEquals(len(amob.scriptsQueue),0)
        self.assertFalse(amob.commandScript)

if __name__ == "__main__":
    unittest.main()

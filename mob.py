#!/usr/bin/env python

import sys
import traceback
import unittest
import pickle
from pymud.chainedmap import ChainedMap
from pymud.coroutine import step
from pymud.interpreter import interpret
from pymud.message import Channel
from pymud.formatter import ColorTextFormatter
from pymud.persist import Persistent, P

def setVariable(self,name,value):
    """Remember something for later"""
    self.variables[name] = value

def say(self,*args):
    """Converse with the locals"""
    self.sendMessage("say",message=" ".join(args),name=self.id)

def look(self,target=None):
    """Look at the world around you"""
    if not self.location():
        self.sendMessage("look",description="eternal nothingness")
    else:
        self.location().seen(self)

def help(self,commandName="help"):
    """Get help on commands"""
    if commandName in self.commands:
        command = self.commands[commandName]
        self.sendMessage("help",name=commandName,help=command.__doc__)
    else:
        self.sendMessage("invalidcommand",name=commandName)

def uber(self):
    """Some uber command"""
    self.sendMessage("action",description="zomg! uber!")

class Mob(Persistent,Channel):

    commands = ChainedMap(map={ 'say':say,
                                'look': look,
                                'help': help,
                                'set':setVariable})
    location = P()
    description = "an ugly son of a mob"

    def __init__(   self,
                    variables=None,
                    commands=None,
                    id=None):
        Persistent.__init__(self)
        Channel.__init__(self)
        self.id = id
        self.deleted = False
        self.currentScript = None
        self.commandQueue = []
        self.location = P()
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
        self.currentScript = None

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['currentScript']
        return state

    def applyCommand(self,command,arguments=[]):
        func = self.commands[command]
        if hasattr(func,'im_self') and func.im_self:
            func(*arguments)
        else:
            func(*[self] + arguments)

    def run(self,n=1):
        #print 'run %s' % self.id
        for x in xrange(n):
            try:
                if not self.currentScript and len(self.commandQueue):
                    self.currentScript = interpret(self.commandQueue.pop(0),self)
                if self.currentScript:
                    if not step(self.currentScript):
                        self.currentScript = None
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
        self.assertFalse(amob.currentScript)
        self.assertEquals(len(amob.commandQueue),3)
        amob.run()
        self.assertEquals(len(amob.commandQueue),2)
        self.assertFalse(amob.currentScript)
        amob.run()
        self.assertEquals(len(amob.commandQueue),1)
        self.assertFalse(amob.currentScript)
        amob.run()
        self.assertEquals(len(amob.commandQueue),0)
        self.assertFalse(amob.currentScript)
        amob.run()
        self.assertEquals(len(amob.commandQueue),0)
        self.assertFalse(amob.currentScript)

if __name__ == "__main__":
    unittest.main()

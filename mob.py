#!/usr/bin/env python

import sys
import unittest
import pickle
from pymud.chainedmap import ChainedMap
from pymud.coroutine import step
from pymud.interpreter import interpret
from pymud.message import Channel, Message
from pymud.formatter import ColorTextFormatter

def setVariable(self,name,value):
    self.variables[name] = value

def say(self,*args):
    self.sendMessage(Message("say",message=" ".join(args),name=self.id))

def uber(self):
    sys.stdout.write("UBER!")
    sys.stdout.flush()

class Mob(Channel):

    commands = ChainedMap({'say':say,
                            'set':setVariable})
    def __init__(   self,
                    variables=None,
                    commands=None,
                    id=None):
        Channel.__init__(self)
        self.id = id
        self.deleted = False
        self.currentScript = None
        self.commandQueue = []
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
        try:
            if not self.currentScript and len(self.commandQueue):
                self.currentScript = interpret(self.commandQueue.pop(-1),self)
            if self.currentScript:
                if not step(self.currentScript):
                    self.currentScript = None
        except Exception, e:
            self.sendMessage(Message("error",error=str(e)))

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

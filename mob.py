#!/usr/bin/env python

import sys
import unittest
import pickle
from chainedmap import ChainedMap

def setVariable(self,name,value):
    self.variables[name] = value

def say(self,*args):
    if self.stdout:
        self.stdout.write(" ".join(args) + "\n")
        self.stdout.flush()

def uber(self):
    if self.stdout:
        self.stdout.write("UBER!")
        self.stdout.flush()

class Mob():

    commands = ChainedMap({'say':say,
                            'set':setVariable})

    def __init__(   self,
                    stdin=sys.stdin,
                    stdout=sys.stdout,
                    variables=None,
                    commands=None):
        self.stdin = stdin
        self.stdout = stdout
        if variables:
            self.variables = variables
        else:
            self.variables = {}
        if commands:
            self.commands = commands
        else:
            self.commands = ChainedMap(Mob.commands)

    def default(self,args):
        apply(say,[self] + args)

    def __setstate__(self,state):
        self.__dict__ = state.copy()
        self.commands.parent = self.__class__.commands
        self.stdout = None
        self.stdin = None

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['stdin']
        del state['stdout']
        return state

    def applyCommand(self,command,arguments=[]):
        func = self.commands[command]
        if hasattr(func,'im_self') and func.im_self:
            apply(func,arguments)
        else:
            apply(func,[self] + arguments)


class Test(unittest.TestCase):

    def testSayHi(self):
        amob = Mob()
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
        mob1 = Mob()
        setVariable(mob1,'a','5')
        say(mob1,'hi1')
        self.assertEquals(mob1.variables['a'],'5')
        out = pickle.dumps(mob1,pickle.HIGHEST_PROTOCOL)
        mob2 = pickle.loads(out)
        self.assertEquals(mob2.variables['a'],'5')
        mob2.stdout = sys.stdout
        say(mob2,'hi2')

    def testPickleCommands(self):
        mob1 = Mob()
        mob1.commands['uber'] = uber
        mob1.applyCommand('say',['hi'])
        mob1.applyCommand('uber')
        out = pickle.dumps(mob1,pickle.HIGHEST_PROTOCOL)
        #print out
        mob2 = pickle.loads(out)
        mob2.stdout = sys.stdout
        mob2.applyCommand('say',['hi'])
        mob2.applyCommand('uber')

if __name__ == "__main__":
    unittest.main()

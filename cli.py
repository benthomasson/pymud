#!/usr/bin/env python

import readline
import cmd

import checker
import interpreter
from coroutine import finish

class Mob():

    def __init__(self):
        self.commands = { "set": self.setVariable }
        self.variables = { }

    def setVariable(self,name,value):
        self.variables[name] = value

class Cli(cmd.Cmd):

    prompt = "pymud>"

    def __init__(self,mob):
        cmd.Cmd.__init__(self)
        self.mob = mob

    def onecmd(self,line):
        try:
            checker.check(line + "\n",self.mob.commands,self.mob.variables)
            finish(interpreter.interpret(line + "\n",self.mob.commands,self.mob.variables))
        except Exception,e:
            print str(e)

if __name__ == '__main__':
    Cli(Mob()).cmdloop()



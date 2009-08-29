#!/usr/bin/env python

import readline
import cmd

import sys
import pymud.checker as checker
import pymud.interpreter as interpreter
from pymud.coroutine import finish
from pymud.mob import Mob

class Cli(cmd.Cmd):

    prompt = "pymud>"

    def __init__(self,mob):
        cmd.Cmd.__init__(self,stdin=mob.stdin,stdout=mob.stdout)
        self.mob = mob

    def onecmd(self,line):
        try:
            checker.check(line + "\n",self.mob.commands,self.mob.variables)
            finish(interpreter.interpret(line + "\n",
                                            self.mob,))
        except Exception,e:
            print str(e)

    def completenames(self, *ignored):
        return self.mob.commands.keys()

if __name__ == '__main__':
    Cli(Mob()).cmdloop()



#!/usr/bin/env python

import readline
import cmd

import checker
import interpreter
from coroutine import finish


class Cli(cmd.Cmd):

    prompt = "pymud>"

    def __init__(self):
        self.commands = {}
        self.variables = {}
        cmd.Cmd.__init__(self)

    def onecmd(self,line):
        try:
            checker.check(line,self.commands,self.variables)
            finish(interpreter.interpret(line,self.commands,self.variables))
        except Exception,e:
            print str(e)

if __name__ == '__main__':
    Cli().cmdloop()


#!/usr/bin/env python

import readline
import cmd

import sys
import time
import pymud.checker as checker
import pymud.interpreter as interpreter
import threading
from pymud.coroutine import finish
from pymud.mob import Mob

class Cli(cmd.Cmd):

    prompt = "pymud>"

    def __init__(self,mob):
        cmd.Cmd.__init__(self)
        self.mob = mob
        self.prompt = "%s>" % mob.id

    def onecmd(self,line):
        try:
            if line:
                self.mob.commandQueue.append(line + "\n")
            self.prompt = "%s>" % self.mob.id
        except Exception,e:
            print str(e)

    def completenames(self, *ignored):
        return self.mob.commands.keys()

if __name__ == '__main__':
    m = Mob()
    cli = Cli(m)
    server_thread = threading.Thread(target=cli.cmdloop)
    server_thread.setDaemon(True)
    server_thread.start()

    try:
        while True:
            time.sleep(0.01)
            m.run()
    except BaseException, e:
        print e



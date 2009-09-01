#!/usr/bin/env python

import readline
import cmd

import sys
import time
import pymud.checker as checker
import pymud.interpreter as interpreter
import threading
from pymud.mob import Mob
from pymud.formatter import ColorTextFormatter
from pymud.persist import P, Persistence

class Cli(cmd.Cmd, ColorTextFormatter):

    prompt = "pymud>"

    def __init__(self,mob):
        self.id = "cli"
        cmd.Cmd.__init__(self)
        self.mob = mob
        self.prompt = "%s>" % mob.id
        mob().addListener(self)

    def onecmd(self,line):
        try:
            if line:
                self.mob().commandQueue.append(line + "\n")
            self.prompt = "%s>" % self.mob().id
        except Exception,e:
            print str(e)

    def completenames(self, *ignored):
        return self.mob().commands.keys()

    def receiveMessage(self,message):
        sys.stdout.write("\n")
        sys.stdout.write(self.formatMessage(message))
        sys.stdout.write("\n")
        sys.stdout.write(self.prompt)
        sys.stdout.flush()

def startCli(m):
    cli = Cli(m)
    server_thread = threading.Thread(target=cli.cmdloop)
    server_thread.setDaemon(True)
    server_thread.start()

if __name__ == '__main__':
    P.persist = Persistence("cli_test.db")
    if P.persist.exists("mob"):
        m = P(P.persist.get("mob"))
    else:
        m = P(P.persist.persist(Mob(stdout=None,stdin=None,id="mob")))

    startCli(m)

    try:
        while True:
            time.sleep(0.01)
            m().run()
    except BaseException, e:
        print e

    P.persist.sync(1000)
    P.persist.close()




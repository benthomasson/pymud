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
        self.mob().interface = self
        self.updatePrompt()
        mob().addListener(self)
        self.messages = []
        self.lineMode = self.commandMode
        self.text = None
        self.callBack = None
        self.callBackKWArgs = None
    
    def updatePrompt(self):
        if self.mob().waiting:
            self.prompt = "(%s)%s>" % (self.mob().waiting,self.mob().id)
        else:
            self.prompt = "%s>" % self.mob().id

    def startTextMode(self,func,**kwargs):
        self.text = ""
        self.callBack = func
        self.callBackKWArgs = kwargs
        self.lineMode = self.textMode
        self.prompt = "+" 
        sys.stdout.write("\n")
        sys.stdout.write(self.prompt)
        sys.stdout.flush()

    def startScriptMode(self,func,**kwargs):
        self.text = ""
        self.callBack = func
        self.callBackKWArgs = kwargs
        self.lineMode = self.scriptMode
        self.prompt = "..." 
        sys.stdout.write("\n")
        sys.stdout.write(self.prompt)
        sys.stdout.flush()

    def onecmd(self,line):
        self.lineMode(line)

    def commandMode(self,line):
        try:
            if line:
                self.mob().commandQueue.append(line + "\n")
            self.updatePrompt()
        except Exception,e:
            print str(e)

    def textMode(self,line):
        if "end" == line.strip() or "." == line.strip():
            self.callBackKWArgs.update(text=self.text,self=self.mob())
            self.callBack(**self.callBackKWArgs)
            self.text = None
            self.lineMode = self.commandMode
            self.prompt = "%s>" % self.mob().id
        else:
            self.text += line + "\n"

    def scriptMode(self,line):
        if "end" == line.strip():
            self.callBackKWArgs.update(text=self.text,self=self.mob())
            self.callBack(**self.callBackKWArgs)
            self.text = None
            self.lineMode = self.commandMode
            self.prompt = "%s>" % self.mob().id
        else:
            self.text += line + "\n"

    def completenames(self, text, *ignored):
        return filter(lambda x: x.startswith(text),self.mob().commands.keys())
    
    def completedefault(self, current, full, *ignored):
        try:
            last = full.split(" ")[-1]
            if last.startswith("$"):
                variables = []
                for x in self.mob().variables.keys():
                    if x:
                        variables.append(x)
                return filter(lambda x:x.startswith(last[1:]),variables)
            command = full.split(" ")[0]
            function = self.mob().commands[command]
            if hasattr(function,"tabcomplete"):
                return function.tabcomplete(self.mob(),current,full)
            else:
                return None
        except BaseException,e:
            print e

    def receiveMessage(self,message):
        self.messages.append(message)

    def receiveMessages(self):
        if not self.messages: return
        for message in self.messages:
            sys.stdout.write("\n")
            sys.stdout.write(self.formatMessage(message))
        sys.stdout.write("\n")
        self.updatePrompt()
        sys.stdout.write(self.prompt)
        sys.stdout.flush()
        self.messages = []


def startCli(m):
    cli = Cli(m)
    server_thread = threading.Thread(target=cli.cmdloop)
    server_thread.setDaemon(True)
    server_thread.start()
    return cli

if __name__ == '__main__':
    P.persist = Persistence("cli_test.db")
    if P.persist.exists("mob"):
        m = P(P.persist.get("mob"))
    else:
        m = P(P.persist.persist(Mob(id="mob")))

    cli = startCli(m)

    try:
        while True:
            time.sleep(0.1)
            m().run()
            cli.receiveMessages()
    except BaseException, e:
        print e

    P.persist.sync(1000)
    P.persist.close()




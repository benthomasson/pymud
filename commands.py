"""User commands"""

import unittest
from pymud.exceptions import *
from pymud.container import Container
from pymud.interpreter import interpret

def setVariable(self,name,value):
    """Remember something for later"""
    self.variables[name] = value

def say(self,*args):
    """Converse with the locals"""
    self.sendMessage("yousay",message=" ".join(args),name=self.id)
    if self.location():
        self.location().sendMessage("say",message=" ".join(args),name=self.id,exclude=[self])

def look(self,target=None):
    """Look at the world around you"""
    if not self.location():
        self.sendMessage("look",description="eternal nothingness")
        return
    if not target:
        self.location().seen(self)
        return
    self.location().get(attribute=target)().seen(self)

def help(self,commandName="help"):
    """Get help on commands"""
    if commandName in self.commands:
        command = self.commands[commandName]
        self.sendMessage("help",name=commandName,help=command.__doc__)
    else:
        self.sendMessage("invalidcommand",name=commandName)

def commands(self):
    self.sendMessage("commands",commands=self.commands)

def uber(self):
    """Some uber command"""
    self.sendMessage("action",description="zomg! uber!")

def get(self,target=None):
    """Get something from the current room"""
    if not self.location():
        raise GameException("You are in the void.  There is nothing here.")
    target = self.location().get(attribute=target)()
    target.checkGet(self)
    self.checkHold(target)
    self.add(target)

def drop(self,target=None):
    target = self.get(attribute=target)()
    target.checkDrop(self)
    if self.location():
        self.location().checkHold(target)
        self.location().add(target)
    else:
        self.remove(target)

def inventory(self):
    """See what you are carrying"""
    Container.seen(self,self)

def quit(self):
    if self.interface:
        self.sendMessage("notice",notice="Good bye!")
        self.interface.quit()

def go(self,exit):
    if not self.location():
        self.sendMessage("notice",notice="You cannot leave the void that way.")
        return
    if exit in self.location().exits:
        self.location().exits[exit]().add(self)
        self.sendMessage("notice",notice="You leave %s" % exit)
    else:
        self.sendMessage("notice",notice="You cannot leave that way.")


def do(self,script):
    if script in self.scripts:
        self.backgroundScript = interpret(self.scripts[script],self)
    else:
        raise GameException("Cannot find script %s" % script)


def script(self,script=None,*args):
    if not script:
        self.sendMessage("scripts",scripts=self.scripts)
    self.scripts[script] = " ".join(args) + "\n"

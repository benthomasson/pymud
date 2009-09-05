"""User commands"""

import unittest

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

def uber(self):
    """Some uber command"""
    self.sendMessage("action",description="zomg! uber!")

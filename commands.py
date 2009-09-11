"""User commands"""

import unittest
from pymud.exceptions import *
from pymud.container import Container
from pymud.interpreter import interpret
from pymud.persist import P

def setVariable(self,name=None,value=None):
    """\
    Remember something for later.

    set <variable name> <value> - Set a variable to a value
    set <variable name>         - Clear the value of a variable
    set                         - Display all your variables

    Example:

    set target zombie

    """
    if not name:
        self.sendMessage("variables",variables=self.variables)
        return
    if name and not value:
        del self.variables[name]
        self.sendMessage("notice",notice="Variable %s cleared" % name)
        return
    if name and value:
        self.variables[name] = value
        self.sendMessage("notice",notice="Variable %s set to %s" % (name,value))
        return

def say(self,*args):
    """\
    Converse with the locals. 
    
    Talk to other characters in the room with you.  Messages that do not
    start with another command are treated as talking to others.

    say <mesage>
    <message>

    Example:

    say hello everyone here

    OR

    hello everyone here
    
    """
    self.sendMessage("yousay",message=" ".join(map(str,args)),name=self.id)
    if self.location():
        self.location().sendMessage("say",
                                    message=" ".join(map(str,args)),
                                    name=self.id,
                                    _exclude=[self])


def chat(self,*args):
    """\
    Converse with the globals.

    Chat with everyone on the server.  

    chat <message>

    Example:

    chat hello everyone everywhere

    """
    chat = P.persist.get("globalchat")
    chat.sendMessage(   "chat",
                        message=" ".join(map(str,args)),
                        name=self.id,
                        channel=chat.name)

def look(self,target=None):
    """\
    Look at the world around you.

    Look at the current room you are in, or look at items or characters in that room.

    look
    look <item>
    look <mob>

    Example:

    look apple
    """
    if not self.location():
        self.sendMessage("look",description="eternal nothingness")
        return
    if not target:
        self.location().seen(self)
        return
    self.location().get(attribute=target)().seen(self)

def help(self,commandName="help"):
    """\
    Get help on commands.

    help <command>
    help
    ? <command>
    ?

    Help will print the help for a command or topic. 

    To get a list of commands type: commands.
    """
    if commandName in self.commands:
        command = self.commands[commandName]
        self.sendMessage("help",name=commandName,help=command.__doc__)
    else:
        self.sendMessage("invalidcommand",name=commandName)

def commands(self):
    """\
    Print a list of commands for your character.

    commands

    """
    self.sendMessage("commands",commands=self.commands)

def uber(self):
    """\
    Some uber command.
    """
    self.sendMessage("action",description="zomg! uber!")

def get(self,target=None):
    """\
    Get something from the current room.

    get <item>

    """
    if not self.location():
        raise GameException("You are in the void.  There is nothing here.")
    target = self.location().get(attribute=target)()
    target.checkGet(self)
    self.checkHold(target)
    self.add(target)

def drop(self,target=None):
    """\
    Drop something from your inventory into the room.

    drop <item>

    """
    target = self.get(attribute=target)()
    target.checkDrop(self)
    if self.location():
        self.location().checkHold(target)
        self.location().add(target)
    else:
        self.remove(target)

def inventory(self):
    """\
    See what you are carrying.

    inventory
    """
    Container.seen(self,self)

def quit(self):
    """\
    Rest your imagination and return to reality.

    quit
    """
    if self.interface:
        self.sendMessage("notice",notice="Good bye!")
        self.interface.quit()

def go(self,exit):
    """\
    Leave through an exit to another room.

    go <exit>

    Example:

    go east
    """
    if not self.location():
        self.sendMessage("notice",notice="You cannot leave the void that way.")
        return
    if exit in self.location().exits:
        self.location().exits[exit]().add(self)
        self.sendMessage("notice",notice="You leave %s" % exit)
    else:
        self.sendMessage("notice",notice="You cannot leave that way.")


def do(self,script=None):
    """\
    Execute a common task.

    Run one of your stored scripts.

    do <name>

    Example:

    do gohome

    """
    if not script:
        self.sendMessage("scriptNames",scripts=self.scripts)
        return
    if script in self.scripts:
        self.scriptsQueue.append(interpret(self.scripts[script],self))
    else:
        raise GameException("Cannot find script %s" % script)


def script(self,script=None):
    """\
    Write or review your scripts.  
    
    Type 'end' on a line by itself to return to the game.

    script          - Review your scripts
    script <name>   - Compose a new named script

    Example:

    script hi
    say hi
    end

    """
    if not script:
        self.sendMessage("scripts",scripts=self.scripts)
        return
    self.interface.startScriptMode(setScript,script=script)

def setScript(self,script,text):
    self.scripts[script] = text
    self.sendMessage("notice",notice="Changed script %s to:\n%s" % (script, text))

def trigger(self,type=None,script=None):
    """\
    Setup a trigger to run a script.  

    Triggers cause a script to be run when something happens.

    trigger <event-name> <script-name>  - Create a new trigger
    trigger <event-name>                - Clear an existing trigger
    trigger                             - Display all your current triggers
    """
    if not type:
        self.sendMessage("triggers",triggers=self.triggers)
        return
    if not script and type in self.triggers:
        del self.triggers[type]
        self.sendMessage("notice",notice="Trigger %s cleared" % type)
        return
    if not script and type not in self.triggers:
        raise GameException("No trigger found named %s" % type)
    if type and script not in self.scripts:
        raise GameException("No script found named %s" % script)
    self.triggers[type] = script
    self.sendMessage("notice",notice="Trigger %s set to run %s" % (type,script))


def description(self):
    """\
    Change the description of your character.

    Type 'end' on a line by itself to finish the description.

    description

    Example:

    description
    a nasty scoundrel
    end

    """
    self.interface.startTextMode(setDescription)

def setDescription(self,text):
    self.detail = text
    self.sendMessage("notice",notice="Changed description to:%s" % text)

def breakCommand(self):
    """\
    Stop doing repetitive things.

    break

    Example:

    loop {
        say hi
        break
    }

    """
    raise BreakException("Stop!")

def stop(self,option=None):
    """\
    Stop what you are doing.

    stop     - Stop your current task.
    stop all - Stop your current task and queued tasks.

    Example:

    loop {
        say hi
    }

    stop all
    """
    if not option:
        self.commandScript = None
        self.waiting = None
        raise BreakException()

    if option == "all":
        self.scriptsQueue = []
        self.commandScript = None
        self.waiting = None
        raise BreakException()

    raise GameException("I dont know how to stop %s" % option)

def wait(self,time=1):
    """\
    Wait for a number of turns.

    wait 
    wait <time>

    Example:

    wait 500
    """
    self.sendMessage("notice",notice="Waiting for %s ticks" % time)
    for x in xrange(int(time),0,-1):
        self.waiting = "Waiting %d" % x
        yield
    self.sendMessage("notice",notice="Finished waiting")
    self.waiting = None



import sys
from chainedmap import ChainedMap

class Mob():

    commands = ChainedMap()

    def __init__(self,stdin=sys.stdin,stdout=sys.stdout):
        self.stdin = stdin
        self.stdout = stdout
        self.variables = {}

    def say(self,*args):
        self.stdout.write(" ".join(args) + "\n")

    def setVariable(self,name,value):
        self.variables[name] = value

Mob.commands.map = {'say':Mob.say,
                    'set':Mob.setVariable}


import code

class Mob():

    def __init__(self):
        self._values = {}
        self._commands = {'__builtins__':None}
        self._commands['abs'] = abs

    def __setitem__(self,key,value):
        self._values[key] = value
    def __getitem__(self,key):
        return self._values[key]

    def mobExec(self,code):
        exec code in self._commands,self

    def mobEval(self,code):
        return eval(code,self._commands,self)

    def do(self):
        print self

    def mobInteract(self):
        code.InteractiveConsole(self._commands).interact('mob')


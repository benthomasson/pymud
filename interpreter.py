#!/usr/bin/env python

import pymud.script as script
import unittest
from pymud.coroutine import coroutine, step, finish
from pymud.exceptions import *

def classname(obj):
    return obj.__class__.__name__

class InterpreterVisitor(object):

    def __init__(self,instance):
        self.instance = instance
        self.commands = instance.commands
        self.variables = instance.variables
        self.conditions = instance.conditions

    def walk(self,ast):
        call = self.visit(ast)
        while step(call): yield

    def visit(self,node,*args):
        fn = getattr(self, 'visit' + classname(node))
        call = fn(node, *args)
        while step(call): yield

    def visitBlock(self,block,*args):
        for statement in block.statements:
            call = self.visit(statement)
            while step(call): yield
        block.value = block.statements[-1].value

    def visitExpressionStatement(self,node,*args):
        """Handles the command statement case and the print statement case"""
        yield
        command = node.expressions[0]
        finish(self.visit(command))
        if command.value in self.commands:
            for expression in node.expressions[1:]:
                finish(self.visit(expression))
            func = self.commands[command.value]
            arguments = map(lambda x: x.value,node.expressions[1:])
            if hasattr(func,'im_self') and func.im_self:
                apply(func,arguments)
            else:
                apply(func,[self.instance] + arguments)
        else:
            for expression in node.expressions[1:]:
                finish(self.visit(expression))
            self.instance.default(map(lambda x: str(x.value),node.expressions))
    
    def visitAssign(self,node,*args):
        yield
        finish(self.visit(node.variable))
        for symbol in node.expression:
            finish(self.visit(symbol))
        self.instance.variables[str(node.variable.value)] = " ".join(map(lambda x:str(x.value),node.expression))

    def visitIfStatement(self,node,*args):
        yield
        finish(self.visit(node.condition))
        if node.condition.value in self.conditions and\
            self.conditions[node.condition.value]:
            call = self.visit(node.script)
            while step(call): yield

    def visitLoopStatement(self,node,*args):
        yield
        try:
            while True:
                call = self.visit(node.script)
                while step(call): yield
        except BreakException,e:
            print str(e)

    def visitSymbol(self,node,*args):
        yield
        node.value = node.name

    def visitVariable(self,node,*args):
        yield
        if node.name in self.variables:
            node.value = self.variables[node.name]
        else:
            node.value = None

@coroutine
def interpret(scriptText,instance):
    block = script.block.parseString(scriptText)
    visitor = InterpreterVisitor(instance)
    call = visitor.walk(block[0])
    while step(call):yield

def say(self,*args):
    print args

def breakCommand(self,*args):
    raise BreakException()

class Test(unittest.TestCase):

    def testStrings(self):
        from pymud.mob import Mob
        finish(interpret("""hello there\n""",Mob(commands={},variables={})))
        finish(interpret("""hello there
line 2
line 3
variable $var
""",Mob(commands={},variables={'var':5})))
        call = interpret("""hello there
line 2
line 3
variable $var
""",Mob(commands={},variables={'var':5}))
        for x in xrange(10):
            print "%s:" % x
            step(call)

    def testCommand(self):
        from pymud.mob import Mob
        finish(interpret("""say hello\n""",Mob(commands={'say':say},variables={})))

    def testIf(self):
        from pymud.mob import Mob
        finish(interpret("""if alive {
say i am alive
}""",Mob(commands={'say':say},variables={})))

    def testLoop(self):
        from pymud.mob import Mob
        finish(interpret("""loop {
say forever
break
}""",Mob(commands={'say':say,'break':breakCommand},variables={})))


if __name__ == '__main__':
    unittest.main()


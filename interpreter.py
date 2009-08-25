#!/usr/bin/env python

import script
import unittest
from coroutine import coroutine, step, finish

def classname(obj):
    return obj.__class__.__name__

class InterpreterVisitor(object):

    def __init__(self,commands,variables):
        self.commands = commands
        self.variables = variables

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
        if self.commands.has_key(command.value):
            for expression in node.expressions[1:]:
                finish(self.visit(expression))
            apply(self.commands[command.value],map(lambda x: x.value,node.expressions[1:]))
        else:
            for expression in node.expressions[1:]:
                finish(self.visit(expression))
            print " ".join(map(lambda x: str(x.value),node.expressions))

    def visitSymbol(self,node,*args):
        yield
        node.value = node.name

    def visitVariable(self,node,*args):
        yield
        if self.variables.has_key(node.name):
            node.value = self.variables[node.name]
        else:
            print None

def interpret(scriptText,commands,variables):
    block = script.block.parseString(scriptText)
    visitor = InterpreterVisitor(commands,variables)
    call = visitor.walk(block[0])
    while step(call):yield

def say(*args):
    print args

class Test(unittest.TestCase):

    def testStrings(self):
        finish(interpret("""hello there\n""",{},{}))
        finish(interpret("""hello there
line 2
line 3
variable $var
""",{},{'var':5}))
        call = interpret("""hello there
line 2
line 3
variable $var
""",{},{'var':5})
        for x in xrange(10):
            print "%s:" % x
            step(call)

    def testCommand(self):
        finish(interpret("""say hello\n""",{'say':say},{}))



if __name__ == '__main__':
    unittest.main()


#!/usr/bin/env python

import script
import unittest
from coroutine import coroutine, step, finish

def classname(obj):
    return obj.__class__.__name__

class InterpreterVisitor(object):

    def __init__(self,instance,commands,variables):
        self.instance = instance
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

    def visitSymbol(self,node,*args):
        yield
        node.value = node.name

    def visitVariable(self,node,*args):
        yield
        if node.name in self.variables:
            node.value = self.variables[node.name]
        else:
            print None

def interpret(scriptText,instance,commands,variables):
    block = script.block.parseString(scriptText)
    visitor = InterpreterVisitor(instance,commands,variables)
    call = visitor.walk(block[0])
    while step(call):yield

def say(self,*args):
    print args

class Test(unittest.TestCase):

    def testStrings(self):
        finish(interpret("""hello there\n""",None,{},{}))
        finish(interpret("""hello there
line 2
line 3
variable $var
""",None,{},{'var':5}))
        call = interpret("""hello there
line 2
line 3
variable $var
""",None,{},{'var':5})
        for x in xrange(10):
            print "%s:" % x
            step(call)

    def testCommand(self):
        finish(interpret("""say hello\n""",None,{'say':say},{}))



if __name__ == '__main__':
    unittest.main()


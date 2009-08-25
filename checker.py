#!/usr/bin/env python

import script
import unittest

class VariableNotSetException(Exception): pass

def classname(obj):
    return obj.__class__.__name__

class CheckerVisitor(object):

    def __init__(self,commands,variables):
        self.commands = commands
        self.variables = variables

    def walk(self,ast):
        self.visit(ast)

    def visit(self,node,*args):
        fn = getattr(self, 'visit' + classname(node))
        fn(node, *args)

    def visitBlock(self,block,*args):
        for statement in block.statements:
            self.visit(statement)
        block.value = block.statements[-1].value

    def visitExpressionStatement(self,node,*args):
        """Handles the command statement case and the print statement case"""
        command = node.expressions[0]
        self.visit(command)
        if self.commands.has_key(command.value):
            for expression in node.expressions[1:]:
                self.visit(expression)
        else:
            for expression in node.expressions[1:]:
                self.visit(expression)

    def visitSymbol(self,node,*args):
        node.value = node.name

    def visitVariable(self,node,*args):
        if self.variables.has_key(node.name):
            node.value = self.variables[node.name]
        else:
            raise VariableNotSetException('Cannot find variable: %s' % node.name)

def check(scriptText,commands,variables):
    block = script.block.parseString(scriptText)
    visitor = CheckerVisitor(commands,variables)
    visitor.walk(block[0])

def say(*args):
    print args

class Test(unittest.TestCase):

    def testStrings(self):
        check("""hello there\n""",{},{})
        check("""hello there
line 2
line 3
variable $var
""",{},{'var':5})
        check("""hello there
line 2
line 3
variable $var
""",{},{'var':5})

    def testCommand(self):
        check("""say hello\n""",{'say':say},{})

    def testVariableFailure(self):
        self.assertRaises(VariableNotSetException,check,"""say hello $var\n""",{'say':say},{})


if __name__ == '__main__':
    unittest.main()


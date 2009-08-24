#!/usr/bin/env python

import script

import unittest

def classname(obj):
    return obj.__class__.__name__

class InterpreterVisitor(object):

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
            print "Calling %s with %s" % (self.commands[command.value],
                map(lambda x: x.value,node.expressions[1:]))
        else:
            for expression in node.expressions[1:]:
                self.visit(expression)
            print " ".join(map(lambda x: str(x.value),node.expressions))

    def visitSymbol(self,node,*args):
        node.value = node.name

    def visitVariable(self,node,*args):
        if self.variables.has_key(node.name):
            node.value = self.variables[node.name]
        else:
            print None

def interpret(scriptText,commands,variables):
    block = script.block.parseString(scriptText)
    visitor = InterpreterVisitor(commands,variables)
    visitor.walk(block[0])
    return block[0].value


class Test(unittest.TestCase):

    def testStrings(self):
        print interpret("""hello there""",{},{})
        print interpret("""hello there
line 2
line 3
variable $var
""",{},{'var':5})


if __name__ == '__main__':
    unittest.main()

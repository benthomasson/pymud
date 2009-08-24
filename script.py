#!/usr/bin/env python

from pyparsing import *
import unittest

class Symbol(object):

    def __init__(self,tokens):
        self.name = tokens[0]
        self.value = None

    def __repr__(self):
        return "Symbol: %s" % self.name

class Variable(object):

    def __init__(self,tokens):
        self.name = tokens[0][1:]
        self.value = None

    def __repr__(self):
        return "Variable: %s" % self.name

class Assign(object):

    def __init__(self,tokens):
        self.variable = tokens[0]
        self.expression = tokens[2:]
        self.value = None

    def __repr__(self):
        return "Assign: %s to %s" % (self.expression, self.variable)

class ExpressionStatement(object):

    def __init__(self,tokens):
        self.expressions = tokens
        self.value = None

    def __repr__(self):
        buf = "Line: "
        buf += ", ".join(map(repr,self.expressions))
        return buf


class Block(object):

    def __init__(self,tokens):
        self.statements = tokens
        self.value = None

    def __repr__(self):
        buf = "Block:\n"
        buf += "\n".join(map(repr,self.statements))
        buf += "\n"
        return buf


ParserElement.setDefaultWhitespaceChars("")

empty = ZeroOrMore(White(" ")).suppress()
word = Word(alphas + nums) + empty
word.setParseAction(Symbol)
variable = Combine( Word("$") + Word(alphas)) + empty
variable.setParseAction(Variable)
expression = OneOrMore(word | variable)
expressionStatement = expression + Optional(White("\n")).suppress()
expressionStatement.setParseAction(ExpressionStatement)
fourSpace = White(" ") + White(" ") + White(" ") + White(" ")
assign = word + Word("=") + empty + expression
assign.setParseAction(Assign)
block = OneOrMore(assign|expressionStatement)
block.setParseAction(Block)

class Test(unittest.TestCase):

    def testSymbol(self):
        print word.parseString('hello')
        print word.parseString('hello there')

    def testVariable(self):
        print variable.parseString('$hello')
        print word.parseString('hello $there')

    def testLine(self):
        print expressionStatement.parseString('hello')
        print expressionStatement.parseString('hello there')
        print expressionStatement.parseString('hello there\nboo')
        print block.parseString('hello there\nboo')
        print expressionStatement.parseString('hello $there everyone')

    def testBlock(self):
        print block.parseString("""hello there
this is the second line
this line contains a $variable
x = $a
""")

    def testAssign(self):
        print assign.parseString("""x = a""")


if __name__ == '__main__':
    unittest.main()

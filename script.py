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

class IfStatement(object):

    def __init__(self,tokens):
        self.condition = tokens[0]
        self.script = tokens[1]
        self.value = None

    def __repr__(self):
        return "if: %s run %s" % (self.condition, self.script)

class LoopStatement(object):

    def __init__(self,tokens):
        self.script = tokens[0]
        self.value = None

    def __repr__(self):
        return "loop: %s" % (self.script)

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

alphanums = alphas + nums
empty = ZeroOrMore(White(" ")).suppress()
word = Combine(Word(alphanums) + Optional(Literal(":") + Word(alphanums))) + empty
word.setParseAction(Symbol)
variable = Combine( Word("$") + Word(alphanums) + Optional(Literal(":") + Word(alphanums))) + empty
variable.setParseAction(Variable)
startStatement = Literal("{") + empty + White("\n").suppress()
endStatement = Literal("}") 
expression = OneOrMore(variable | word)
expressionStatement = expression + empty + White("\n").suppress()
expressionStatement.setParseAction(ExpressionStatement)
assign = word + Word("=") + empty + expression
assign.setParseAction(Assign)
block = Forward()
script = startStatement.suppress() + block + endStatement.suppress()
ifStatement = Literal("if").suppress() + empty + word + script
ifStatement.setParseAction(IfStatement)
loopStatement = Literal("loop").suppress() + empty + script
loopStatement.setParseAction(LoopStatement)
block << OneOrMore(loopStatement|ifStatement|assign|expressionStatement)
block.setParseAction(Block)

class Test(unittest.TestCase):

    def testSymbol(self):
        print word.parseString('hello')
        print word.parseString('hello there')

    def testVariable(self):
        print variable.parseString('$hello')
        print word.parseString('hello $there')
        print variable.parseString('$namespace:hello')

    def testExpression(self):
        print expression.parseString('$hello')
        print expression.parseString('hello $there')
        print expression.parseString('hi $namespace:hello')

    def testLine(self):
        print expressionStatement.parseString('hello\n')
        print expressionStatement.parseString('hello there\n')
        print expressionStatement.parseString('hello there\nboo')
        print block.parseString('hello there\nboo')
        print expressionStatement.parseString('hello $there everyone\n')
        print expressionStatement.parseString('hello $t:there everyone\n')

    def testLineComplete(self):
        print expressionStatement.parseString('hello dfdf\n')

    def testBlock(self):
        print block.parseString("""hello there
this is the second line
this line contains a $variable
this line contains a $namespace:variable
x = $a
""")

    def testAssign(self):
        print assign.parseString("""x = a""")

    def testScript(self):
        print script.parseString("""{
hi there
}
""")
        print script.parseString("""{
hi there
}
""")

    def testIfStatement(self):
        print ifStatement.parseString("""if a {

print hi
}""")
        print ifStatement.parseString("""if b {
print hi

}""")

        print block.parseString("""if c {
print hi there

}""")


    def testLoopStatement(self):
        print loopStatement.parseString("""loop {

print hi
}""")


if __name__ == '__main__':
    unittest.main()

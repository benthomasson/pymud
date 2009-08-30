#!/usr/bin/env python

import unittest

from pymud.colors import colors, nocolors

class TextFormatter(object):

    def formatMessage(self,message):
        message.dict.update(nocolors)
        fn = getattr(self, 'format' + message.type)
        return fn(message)

    def formatsay(self,message):
        return "%(WHITE)s%(name)s says %(BLUE)s'%(message)s'%(CLEAR)s" % message.dict

class ColorTextFormatter(TextFormatter):

    def formatMessage(self,message):
        message.dict.update(colors)
        fn = getattr(self, 'format' + message.type)
        return fn(message)

class Test(unittest.TestCase):

    def test(self):
        from message import Message
        tf = TextFormatter()
        ctf = ColorTextFormatter()
        m = Message("say",message="hello",name="Ed",id="1")
        print tf.formatMessage(m)
        print ctf.formatMessage(m)

if __name__ == "__main__":
    unittest.main()

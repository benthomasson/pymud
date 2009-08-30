#!/usr/bin/env python

import unittest


class Message(object):

    def __init__(self,type,**kwargs):
        self.type = type
        self.dict = kwargs


class Test(unittest.TestCase):

    def test(self):
        m = Message("say",message="hello",name="Ed",id="1")
        print "%(name)s says '%(message)s'" % m.dict


if __name__ == "__main__":
    unittest.main()
    

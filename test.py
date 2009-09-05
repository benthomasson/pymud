#!/usr/bin/env python

import unittest

import mob
import persist
import chainedmap
import checker
import formatter
import interpreter
import message
import scheduler
import script
import container

class SimpleSuite(unittest.TestSuite):

    def __init__(self,*args,**kwargs):
        unittest.TestSuite.__init__(self,*args,**kwargs)
        self.loader = unittest.TestLoader()
    
    def addTestsFromTestCase(self,klass):
        self.addTests(self.loader.loadTestsFromTestCase(klass))

    def runSelf(self):
        unittest.TextTestRunner(verbosity=2).run(suite)

suite = SimpleSuite()
map(suite.addTestsFromTestCase,[mob.Test,
                                persist.TestPersistence,
                                persist.TestShelve,
                                persist.TestP,
                                chainedmap.Test,
                                checker.Test,
                                formatter.Test,
                                interpreter.Test,
                                message.TestMessage,
                                message.TestChannel,
                                scheduler.Test,
                                script.Test,
                                container.Test,
                                ])


if __name__ == "__main__":
   suite.runSelf()

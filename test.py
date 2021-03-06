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
import testfixture
import null
import rule
import choices

class SimpleSuite(unittest.TestSuite):

    def __init__(self,*args,**kwargs):
        unittest.TestSuite.__init__(self,*args,**kwargs)
        self.loader = unittest.TestLoader()
    
    def addTestsFromTestCase(self,klass):
        self.addTests(self.loader.loadTestsFromTestCase(klass))

    def addTestsFromModule(self,module):
        if type(module) == type(""):
            exec "import %s" % module
            module = eval(module)
        self.addTests(self.loader.loadTestsFromModule(module))

    def runSelf(self):
        unittest.TextTestRunner(verbosity=2).run(suite)

suite = SimpleSuite()
map(suite.addTestsFromTestCase,[mob.Test,
                                persist.TestPersistence,
                                persist.TestShelve,
                                persist.TestP,
                                persist.TestMockPersistence,
                                chainedmap.Test,
                                chainedmap.TestMultipleMap,
                                checker.Test,
                                formatter.Test,
                                interpreter.Test,
                                message.TestMessage,
                                message.TestChannel,
                                scheduler.Test,
                                script.Test,
                                container.Test,
                                container.TestSlotted,
                                null.Test,
                                testfixture.TestTestFixture,
                                rule._TestRules,
                                rule._TestSteppableRule,
                                choices._Test,
                                ])

map(suite.addTestsFromModule,[ 'pymud.tests.chat',
                               'pymud.tests.commands',
                                ])

if __name__ == "__main__":
   suite.runSelf()

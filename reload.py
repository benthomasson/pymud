#!/usr/bin/env python

import unittest
import sys
import __builtin__

class RollbackImporter:
    def __init__(self):
        "Creates an instance and installs as the global importer"
        self.previousModules = sys.modules.copy()
        self.realImport = __builtin__.__import__
        __builtin__.__import__ = self._import
        self.newModules = {}
        
    def _import(self, name, globals=None, locals=None, fromlist=[],level=-1):
        result = apply(self.realImport, (name, globals, locals, fromlist,level))
        self.newModules[name] = 1
        return result
        
    def uninstall(self):
        for modname in self.newModules.keys():
            if not self.previousModules.has_key(modname):
                # Force reload when modname next imported
                if modname.startswith("pymud"):
                    del(sys.modules[modname])
                    print modname
        #__builtin__.__import__ = self.realImport


rollbackImporter = RollbackImporter()

class TestReload(unittest.TestCase):

    def test(self):
        import cli
        self.assert_('cli' in sys.modules)
        rollbackImporter.uninstall()
        self.assertFalse('cli' in sys.modules)
        import cli
        self.assert_('cli' in sys.modules)

if __name__ == "__main__":
    unittest.main()


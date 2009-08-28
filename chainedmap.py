#!/usr/bin/env python

from collections import MutableMapping
import unittest
import pickle

class ChainedMap(MutableMapping):

    def __init__(self,parent=None,map=None):
        self.parent = parent
        if map:
            self.map = map
        else:
            self.map = {}

    def __iter__(self):
        for x in self.map:
            yield x
        if self.parent:
            for x in self.parent:
                yield x

    def __len__(self):
        length = len(self.map) 
        if self.parent:
            length += len(self.parent)
        return length

    def __setitem__(self,key,value):
        self.map[key] = value

    def __delitem__(self,key):
        del self.map[key]

    def __getitem__(self,key):
        try:
            return self.map[key]
        except KeyError:
            pass
        if self.parent:
            return self.parent[key]
        else:
            raise KeyError, key

    def __contains__(self,key):
        try:
            self[key]
            return True
        except KeyError:
            return False

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['parent']
        return state

    def __setstate__(self,state):
        self.__dict__ = state.copy()
        self.parent = None
        return state
        


class Test(unittest.TestCase):

    def testSingleRead(self):
        cmap = ChainedMap(map={"a":1})
        self.assertEquals(cmap['a'],1)
        self.assertRaises(KeyError,cmap.__getitem__,'b')
        self.assert_('a' in cmap)
        self.assertFalse('b' in cmap)
        self.assertEquals(len(cmap),1)

    def testParentRead(self):
        pcmap = ChainedMap(map={"a":1})
        ccmap = ChainedMap(parent=pcmap,map={'z':10})
        self.assertEquals(ccmap['a'],1)
        self.assertRaises(KeyError,ccmap.__getitem__,'b')
        self.assert_('a' in ccmap)
        self.assertFalse('b' in ccmap)
        self.assert_('z' in ccmap)
        self.assertEquals(len(pcmap),1)
        self.assertEquals(len(ccmap),2)
    
    def testSingleWrite(self):
        cmap = ChainedMap(map={"a":1})
        self.assertEquals(cmap['a'],1)
        cmap['a'] = 2
        self.assertEquals(cmap['a'],2)
        del cmap['a']
        self.assertRaises(KeyError,cmap.__getitem__,'a')

    def testParentWrite(self):
        pcmap = ChainedMap(map={"a":1})
        ccmap = ChainedMap(parent=pcmap,map={'z':10})
        self.assertEquals(ccmap['a'],1)
        ccmap['a'] = 2
        self.assertEquals(ccmap['a'],2)
        self.assertEquals(pcmap['a'],1)
        del ccmap['a']
        self.assertEquals(ccmap['a'],1)
        self.assertEquals(pcmap['a'],1)
        del pcmap['a']
        self.assertRaises(KeyError,ccmap.__getitem__,'a')
        self.assertRaises(KeyError,pcmap.__getitem__,'a')

    def testPickle(self):
        cmap1 = ChainedMap(map={"a":1})
        out = pickle.dumps(cmap1,2)
        cmap2 = pickle.loads(out)
        self.assertFalse(cmap1 is cmap2)
        self.assertEquals(cmap1['a'],1)
        self.assertEquals(cmap2['a'],1)
 
    def testParentNotPickle(self):
        pcmap = ChainedMap(map={"a":1})
        ccmap = ChainedMap(parent=pcmap,map={'z':10})
        out = pickle.dumps(ccmap,2)
        cmap2 = pickle.loads(out)
        self.assertFalse(cmap2 is ccmap)
        self.assert_(ccmap.parent)
        self.assertFalse(cmap2.parent)
    
if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python

from multiprocessing.managers import BaseManager, Process
from threading import Thread
from proxy import SimProxy
from pymud.persist import P, Persistence, getP
import time

import unittest
from testfixture import RoomTestFixture

class ProxyManager(BaseManager): pass

ProxyManager.register('get_sim',proxytype=SimProxy)

class ProxyPersistence(object):

    manager = None

    def __init__(self):
        pass

    def get(self,id):
        return self.manager.get_sim(id)

class Test(RoomTestFixture):

    def startServer(self):
        print 'startServer'
        import proxyserver
        from pymud.mob import Mob
        mob = self.createHere("mob",Mob)
        m2 = P.persist.get("mob")
        self.assert_(mob is m2)
        print mob,repr(mob)
        print P.persist
        proxyserver.startServer(ThreadOrProcess=None)

    def test(self):
        from pymud.mob import Mob
        thread = Process(target=self.startServer)
        thread.daemon = True
        thread.start()
        #thread.join()
        time.sleep(1)
        #self.startServer()
        client = ProxyManager(address=("",6000),authkey="abc")
        ProxyPersistence.manager = client
        P.persist = ProxyPersistence()
        client.connect()
        print P.persist
        s = client.get_sim("mob")
        self.assertEquals(s.description,'an ugly son of a mob')
        print s,repr(s)
        loc = s.location
        self.assertFalse(loc.ref)
        self.assertEquals(loc.id,'world')
        print repr(s.location)
        print repr(s.location())
        print str(s.location)
        print str(s.location())


if __name__ == "__main__":
    unittest.main()

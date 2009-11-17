#!/usr/bin/env python

import unittest
from multiprocessing.managers import BaseManager
from threading import Thread
from sim import Sim
from pymud.persist import P, Persistence, getP

from proxy import SimProxy
from testfixture import RoomTestFixture

def get_sim(id):
    return P.persist.get(id)

class ProxyManager(BaseManager): pass

ProxyManager.register('get_sim',get_sim,proxytype=SimProxy)

def startServer(address=("",6000)):
    manager = ProxyManager(address=address,authkey='abc')
    server = manager.get_server()
    thread = Thread(target=server.serve_forever)
    thread.start()

class Test(RoomTestFixture):

    def test(self):
        from pymud.mob import Mob
        mob = self.createHere("mob",Mob)
        m2 = P.persist.get("mob")
        self.assert_(mob is m2)
        import proxyclient
        startServer()
        client = proxyclient.ProxyManager(address=("localhost",6000),authkey="abc")
        client.connect()
        s = client.get_sim("mob")
        self.assertEquals(s.description,'an ugly son of a mob')
        print mob,repr(mob),s,repr(s)
        loc = s.location
        self.assertFalse(loc.ref)
        self.assertEquals(loc.id,'world')
        print repr(s.location)
        print repr(s.location())
        

if __name__ == "__main__":
    unittest.main()

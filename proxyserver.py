#!/usr/bin/env python

import unittest
from multiprocessing.managers import BaseManager
from threading import Thread
from sim import Sim

from proxy import SimProxy

def get_sim(id):
    return Sim()

class ProxyManager(BaseManager): pass

ProxyManager.register('get_sim',get_sim,proxytype=SimProxy)

def startServer(address=("",6000)):
    manager = ProxyManager(address=address,authkey='abc')
    server = manager.get_server()
    thread = Thread(target=server.serve_forever)
    thread.start()

class Test(unittest.TestCase):

    def test(self):
        import proxyclient
        startServer()
        client = proxyclient.ProxyManager(address=("localhost",6000),authkey="abc")
        client.connect()
        s = client.get_sim(0)
        self.assertEquals(s.description,'something')
        

if __name__ == "__main__":
    unittest.main()

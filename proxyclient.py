
from multiprocessing.managers import BaseManager
from proxy import SimProxy

class ProxyManager(BaseManager): pass

ProxyManager.register('get_sim',proxytype=SimProxy)



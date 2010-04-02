
import unittest

import shelve
import redis,redis.client
import pickle
import sys
import os
from pymud.coroutine import coroutine,step,finish
from pymud.formatter import ColorTextFormatter
from collections import MutableMapping

def getP(o):
    if o.id in P.instances:
        return P.instances[o.id]
    else:
        p = P(o)
        P.instances[o.id] = p
        return p

class P(object):
    """P is a persistent reference to a persistent object.
    To create a new persistent reference use:
    
    >>> x = persist.P(o).

    To retrieve the object from the peristent reference above use:

    >>> x()
    """

    persist = None
    instances = {}

    __slots__ = ['id','ref']

    def __init__(self,o=None):
        if not o:
            self.id = None
            self.ref = None
        elif isinstance(o,P):
            self.id = o.id
            self.ref = o()
        else:
            self.id = o.id
            self.ref = o
        P.instances[self.id] = self

    def __call__(self):
        if self.ref and not hasattr(self.ref,'deleted'):
            return self.ref
        if self.ref and not self.ref.deleted:
            return self.ref
        if self.ref and self.ref.deleted:
            return None
        if not self.id: return None
        try:
            self.ref = P.persist.get(self.id)
            return self.ref
        except KeyError,e:
            return None

    def __eq__(self,other):
        return self.id == other.id

    def __nonzero__(self):
        return self() != None

    def delete(self):
        del P.instances[self.id]
        P.persist.delete(self)
        self.id = None
        self.ref = None

    def __setstate__(self,state):
        self.id = state['id']
        self.ref = None

    def __getstate__(self):
        state = {}
        state['id'] = self.id
        return state

    def __str__(self):
        return "P" + str(self())

    def __repr__(self):
        return "P" + repr(self())

P.null = P()

class RedisShelve(MutableMapping):

    shelves = {}

    @classmethod
    def getShelve(cls,db=0):
        if db not in cls.shelves:
            cls.shelves[db] = cls(db)
        return  cls.shelves[db]

    def __init__(self,db=0):
        self.redis_conn = redis.Redis(db=db)
        self.cache = {}

    def __iter__(self):
        for x in self.redis_conn.keys():
            yield x

    def __len__(self):
        return len(self.redis_conn.keys())

    def __setitem__(self,key,value):
        self.cache[key] = value
        self.redis_conn.set(key,pickle.dumps(value))

    def __delitem__(self,key):
        if key in self.cache:
            del self.cache[key]
        self.redis_conn.delete(key)

    def __getitem__(self,key):
        if key in self.cache:
            return self.cache[key]
        p = self.redis_conn.get(key)
        if p:
            return pickle.loads(p)
        else:
            raise KeyError, key

    def __contains__(self,key):
        if key in self.cache:
            return True
        p = self.redis_conn.get(key)
        if p:
            return True
        else:
            return False
    
    def save(self):
        self.redis_conn.save()

    def bgsave(self):
        try:
            self.redis_conn.bgsave()
        except redis.client.ResponseError,e:
            pass

class Persistence(object):

    def __init__(self,db):
        self.db = RedisShelve.getShelve(db=db)
        if '0' in self.db:
            self.id = self.db['0']
        else:
            self.id = 0
        self.db['0'] = self.id

    def getNextId(self):
        self.id += 1
        self.db['0'] = self.id
        return self.id

    def persist(self,o):
        if not o.id:
            o.id = "%x" % self.getNextId()
        self.db[o.id] = o
        return o

    def get(self,id):
        return self.db[id]

    def getOrCreate(self,id,klass,*args,**kwargs):
        if self.exists(id):
            return self.get(id)
        else:
            instance = klass(id=id,*args,**kwargs)
            self.persist(instance)
            return instance

    def exists(self,id):
        try:
            self.db[id]
            return True
        except KeyError, e:
            return False

    def delete(self,o):
        if o.id in self.db:
            self.db[o.id].deleted = True
            del self.db[o.id]

    def sync(self):
        self.db.bgsave()

    def syncAll(self):
        self.db.save()

    def run(self,n=1):
        self.sync()

class MockPersistence(Persistence):

    def __init__(self):
        self.db = {}
        if '0' in self.db:
            self.id = self.db['0']
        else:
            self.id = 0
        self.db['0'] = self.id

    def sync(self,n=1):
        pass

    def syncAll(self):
        pass

    @coroutine
    def partialSync(self):
        yield

    def close(self):
        pass

class Persistent(object):

    def __init__(self):
        self.id = None
        self.deleted = False

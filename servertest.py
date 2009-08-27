#!/usr/bin/env python

from multiprocessing import Process

import socket

def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost',8000))
    for x in xrange(10):
        s.send('Hello world\n')
        data = s.recv(1024)
        print 'Received:', data
    s.close()

if __name__ == '__main__':
    for x in xrange(10):
        p = Process(target=connect)
        p.start()
    p.join()


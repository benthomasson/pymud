#!/usr/bin/env python

import readline
import cmd


class Cli(cmd.Cmd):

    def do_hello(self,stuff):
        print "Hello %s" % stuff

    def do_help(self,cmd):
        print 'Hi %s' % cmd

if __name__ == '__main__':
    Cli().cmdloop("Hi there")


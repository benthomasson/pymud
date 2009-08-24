
import thread
import time

def alarm(secs):
    def wait(secs):
        for n in xrange(secs):
            time.sleep(1)
            print 'Zzzzz....'
        thread.interrupt_main()
    thread.start_new_thread(wait, (secs,))


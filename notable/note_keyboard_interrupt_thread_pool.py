#!/usr/bin/env python

#!/usr/bin/env python

# Copyright (c) 2011 John Reese
# Licensed under the MIT License

import os
import time
import signal
import multiprocessing

def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def run_worker():
    print 'A worker started with its 15sec'
    time.sleep(15)
    print 'A worker is done with its 15sec'

def main():
    print "Initializing 5 workers"
    pool = multiprocessing.Pool(5, init_worker)

    print "Starting 3 jobs of 15 seconds each"
    for i in range(3):
        pool.apply_async(run_worker)

    try:
        print "Waiting 10 seconds"
        time.sleep(10)
        print "Done waiting 10 seconds"

    except KeyboardInterrupt:
        print " Caught KeyboardInterrupt, terminating workers"
        pool.terminate()
        pool.join()

    else:
        print "Quitting normally"
        pool.close()
        pool.join()

if __name__ == "__main__":
    main()
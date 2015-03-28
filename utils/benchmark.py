#!/usr/bin/env python

from time import time

## simple timing-based benchmark class
#BENCH_TOTAL = 0
#BENCH_COUNT = 0
#def benchmark(startTime):
#    global BENCH_COUNT, BENCH_TOTAL
#    BENCH_COUNT = BENCH_COUNT + 1
#    BENCH_TOTAL = BENCH_TOTAL + (time() - startTime)

# simple timing-based benchmark
class Benchmark(object):
    """simple timing-based benchmark"""
    
    def __init__(self, label):
        self.label = label
        self.totalsec = 0.0
        self.count = 0
        # reverse polarity so the data takes over these roles
        # also do this "smartly" to avoid computational overhead
        self.min = 1e6
        self.max = -1
        
    def __str__(self):
        avg = self.get_stats()
        fmt = 'benchmark (sec) {0:s}: count = {1:d}, min/avg/max = {2:.1f} / {3:.1f} / {4:.1f}, total = {5:.1f}s'
        return fmt.format(self.label, self.count, self.min, avg, self.max, self.totalsec)
                
    def start(self):
        self.start_time = time()
        
    def get_stats(self):
        self.count += 1
        sec_since_start = time() - self.start_time
        self.totalsec += sec_since_start
        if sec_since_start < self.min:
            self.min = sec_since_start
        if sec_since_start > self.max:
            self.max = sec_since_start
        return self.totalsec / self.count

def demo():
    from time import sleep
    bm = Benchmark('demo')
    for i in range(2,0,-1):
        bm.start()
        sleep(i)
        print bm
    print '- - -'
    for i in range(3,6):
        bm.start()
        sleep(i)
        print bm

if __name__ == "__main__":
    demo()
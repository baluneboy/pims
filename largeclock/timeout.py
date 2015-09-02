#!/usr/bin/env python

from multiprocessing import Process, Queue
from time import sleep

def query_fun_example(query, out_q):
    sleep(0.5)
    out_q.put(query)

def run_with_timeout(func, timeout_sec, args, kwargs):
    """Runs a function with time limit
    
    :param func: The function to run
    :param args: The functions arguments as a tuple
    :param kwargs: The functions keyword args as a dict
    :param timeout_sec: The time limit in seconds
    :return: True if func ended successfully; otherwise False
    """
    p = Process(target=func, args=args, kwargs=kwargs)
    p.start()
    p.join(timeout_sec)
    if p.is_alive():
        p.terminate()
        return False
    
    return True
    
if __name__ == "__main__":
           
    timeout_sec = 3.5
    out_q1 = Queue()
    args = ('query', out_q1)
    kwargs = {}
    finished = run_with_timeout(query_fun_example, timeout_sec, args, kwargs)
    print "timeout_sec = ", timeout_sec, 
    if finished:
        if out_q1.empty():
            print 'empty'
        else:
            print 'got results', out_q1.get()
    else:
        print 'timeout_sec'

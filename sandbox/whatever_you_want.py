#!/usr/bin/env python

import resource
import time

from stoppable_thread import StoppableThread

class MyLibrarySniffingClass(StoppableThread):
    def __init__(self, target_lib_call, arg1, arg2):
        super(MyLibrarySniffingClass, self).__init__()
        self.target_function = target_lib_call
        self.arg1 = arg1
        self.arg2 = arg2
        self.results = None

    def startup(self):
        # Overload the startup function
        print "Calling the Target Library Function..."

    def cleanup(self):
        # Overload the cleanup function
        print "Library Call Complete"

    def mainloop(self):
        # Start the library Call
        self.results = self.target_function(self.arg1, self.arg2)

        # Kill the thread when complete
        self.stop()

def SomeLongRunningLibraryCall(arg1, arg2):
    max_dict_entries = 2500
    delay_per_entry = .005

    some_large_dictionary = {}
    dict_entry_count = 0

    while(1):
        time.sleep(delay_per_entry)
        dict_entry_count += 1
        some_large_dictionary[dict_entry_count]=range(10000)

        if len(some_large_dictionary) > max_dict_entries:
            break

    print arg1 + " " +  arg2
    return "Good Bye World"

if __name__ == "__main__":
    # Lib Testing Code
    mythread = MyLibrarySniffingClass(SomeLongRunningLibraryCall, "Hello", "World")
    mythread.start()

    start_mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    delta_mem = 0
    max_memory = 0
    memory_usage_refresh = .005 # Seconds

    while(1):
        time.sleep(memory_usage_refresh)
        delta_mem = (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) - start_mem
        if delta_mem > max_memory:
            max_memory = delta_mem

        # Uncomment next line to see the memory usuage during run-time 
        #print "Memory Usage During Call: %d MB" % (delta_mem / 1000000.0)

        # Check to see if the library call is complete
        if mythread.isShutdown():
            print mythread.results
            break;

    print "\nMAX Memory Usage in MB: " + str(round(max_memory / 1024.0, 3))

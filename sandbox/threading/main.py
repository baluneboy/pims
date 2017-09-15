import os
import Queue
from worker import WorkerThread


def main(args):
    # Create a single input and a single output queue for all threads.
    dir_q = Queue.Queue()
    result_q = Queue.Queue()

    # Create the "thread pool"
    pool = [WorkerThread(dir_q=dir_q, result_q=result_q) for _ in range(4)]

    # Start all threads
    for thread in pool:
        thread.start()

    # Give the workers some work to do
    work_count = 0
    for my_dir in args:
        if os.path.exists(my_dir):
            work_count += 1
            dir_q.put(my_dir)

    print 'Assigned %s dirs to workers' % work_count

    # Now get all the results
    while work_count > 0:
        # Blocking 'get' from a Queue.
        result = result_q.get()
        print 'From thread %s: %s files found in dir %s' % (
            result[0], len(result[2]), result[1])
        work_count -= 1

    # Ask threads to die and wait for them to do it
    for thread in pool:
        thread.join()


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
import multiprocessing
import time


def bar(n, foo='mine'):
    for i in range(n):
        print("Tick #%03d (%s)" % (i, foo))
        time.sleep(1)


if __name__ == '__main__':
    # Start bar as a process
    # p = multiprocessing.Process(target=bar, args=(10,), kwargs={'foo': 'bah'})
    p = multiprocessing.Process(target=bar, args=(8,))
    p.start()

    # Wait for 10 seconds or until process finishes
    p.join(10)

    # If thread is still active
    if p.is_alive():
        print("running... let's kill it...")

        # Terminate
        p.terminate()
        p.join()
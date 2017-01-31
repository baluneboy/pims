# Create a server for a single shared fifo which remote clients can access:
from multiprocessing.managers import BaseManager
from fifo import FIFOBuffer
fifo = FIFOBuffer()
class FIFOManager(BaseManager): pass
FIFOManager.register('get_fifo', callable=lambda:fifo)
m = FIFOManager(address=('', 50000), authkey='abracadabra')
s = m.get_server()
#s.serve_forever()
s.start()

# One client can access the server as follows:
from multiprocessing.managers import BaseManager
import numpy as np
class FIFOManager(BaseManager): pass
FIFOManager.register('get_fifo')
m = FIFOManager(address=('jimmy', 50000), authkey='abracadabra')
m.connect()
fifo = m.get_fifo()
fifo.initialize( (9,4) )
fifo.append( np.zeros( (3, 4) ) )
fifo.append( np.ones( (3, 4) ) )

# Another client can also use it:
from multiprocessing.managers import BaseManager
class FIFOManager(BaseManager): pass
FIFOManager.register('get_fifo')
m = FIFOManager(address=('jimmy', 50000), authkey='abracadabra')
m.connect()
fifo = m.get_fifo()
print fifo.array()
#!/usr/bin/env python

from pydispatch import dispatcher
SIGNAL = 'my-first-signal'

def handle_event( sender ):
    """Simple event handler"""
    print 'Signal was sent by', sender
dispatcher.connect( handle_event, signal=SIGNAL, sender=dispatcher.Any )

first_sender = object()
second_sender = {}
def main( ):
    dispatcher.send( signal=SIGNAL, sender=first_sender )
    dispatcher.send( signal=SIGNAL, sender=globals() )
    
if __name__ == '__main__':
    main()
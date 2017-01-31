#!/usr/bin/env python

usage = """Usage:
python example-service.py &
python example-async-client.py
python example-client.py --exit-service"""

import sys
import traceback
import gobject
import dbus
import dbus.mainloop.glib

# Callbacks for asynchronous calls

def handle_hello_reply(r):
    global loop
    print str(r) # note: this goes to service's stdout [I think?]
    loop.quit()

def handle_hello_error(e):
    global loop
    print "HelloWorld raised an exception! That's not meant to happen..."
    print "\t", str(e)
    loop.quit()

def handle_raise_reply():
    global loop
    print "RaiseException returned normally! That's not meant to happen..."
    loop.quit()

def handle_raise_error(e):
    global loop
    print "RaiseException raised an exception as expected:"
    print "\t", str(e)
    loop.quit()

def call_hello(remote_object):
    # To make an async call, use the reply_handler and error_handler kwargs
    remote_object.HelloWorld("Hello from example-async-client.py!",
                             dbus_interface='com.example.SampleInterface',
                             reply_handler=handle_hello_reply,
                             error_handler=handle_hello_error)
    return False

def call_raise(remote_object):
    # Interface objects also support async calls
    iface = dbus.Interface(remote_object, 'com.example.SampleInterface')
    iface.RaiseException(reply_handler=handle_raise_reply,
                         error_handler=handle_raise_error)
    return False

def call_both():
    global loop
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()
    try:
        remote_object = bus.get_object("com.example.SampleService","/SomeObject")
    except dbus.DBusException:
        traceback.print_exc()
        print usage
        sys.exit(1)
    
    # Make the hello method call after a short delay
    gobject.timeout_add(100, call_hello, remote_object)
    loop = gobject.MainLoop()
    loop.run()
    
    # Make the raise method call after a short delay
    gobject.timeout_add(100, call_raise, remote_object)
    loop = gobject.MainLoop()
    loop.run()

if __name__ == '__main__':
    call_both()
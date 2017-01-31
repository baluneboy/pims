#!/usr/bin/python
import gobject
import dbus.service
import time
from dbus.glib import DBusGMainLoop

# FIXME
print 'cannot figure out how to make call to AsyncSleep or AsyncMethod other than from d-feet dialog!?'
raise SystemExit

BUS='gov.nasa.grc.pims.Monitor'
PATH='/gov/nasa/grc/pims/Monitor'
IFACE='gov.nasa.grc.pims.Monitor'
START_TIME=time.time()

def heartbeat():
    print "Still alive at", time.time() - START_TIME
    return True

class Monitor(dbus.service.Object):

    def __init__(self):
        self.bus = dbus.SessionBus()
        bus_name = dbus.service.BusName(BUS, bus=self.bus)
        dbus.service.Object.__init__(self, bus_name, PATH)

    @dbus.service.method(dbus_interface=IFACE,
                         in_signature='s', out_signature='as')
    def HelloWorld(self, hello_message):
        print (str(hello_message))
        return ["Hello", " from example-service.py", "with unique name", self.bus.get_unique_name()]

    @dbus.service.method(dbus_interface=IFACE,
                         in_signature='', out_signature='(ss)')
    def GetTuple(self):
        return ("Hello Tuple", " from example-service.py")

    @dbus.service.method(dbus_interface=IFACE,
                         in_signature='', out_signature='a{ss}')
    def GetDict(self):
        return {"first": "Hello Dict", "second": " from example-service.py"}

    @dbus.service.method(dbus_interface=IFACE,
                         in_signature='', out_signature='')
    def Exit(self):
        loop.quit()

    @dbus.service.method(dbus_interface=IFACE,
                         in_signature='i',
                         out_signature='i',
                         async_callbacks=('reply_handler', 'error_handler') )
    def AsyncSleep(self, seconds, reply_handler, error_handler):
        print "Sleeping for %ds" % seconds
        gobject.timeout_add_seconds(seconds, lambda: reply_handler(seconds) )

    @dbus.service.method(dbus_interface=IFACE, in_signature='bbv', out_signature='v', async_callbacks=('return_cb', 'error_cb'))
    def AsyncMethod(self, async, fail, variant, return_cb, error_cb):
        try:
            if async:
                gobject.timeout_add(500, self.AsyncMethod, False, fail, variant, return_cb, error_cb)
                return
            else:
                if fail:
                    raise RuntimeError
                else:
                    return_cb(variant)
                return False # do not run again
        except Exception, e:
            error_cb(e)

DBusGMainLoop(set_as_default=True)
loop = gobject.MainLoop()

# Start the heartbeat
handle = gobject.timeout_add_seconds(1, heartbeat)

# Start the D-Bus service
monitor = Monitor()
loop.run()

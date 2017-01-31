#!/usr/bin/env python

usage = """Usage:
python recipes_dbus_service.py &
python recipes_dbus_client.py"""

import sys
import traceback
import dbus

def main():
    
    bus = dbus.SessionBus()
    try:
        remote_object = bus.get_object("gov.pims.SamsService","/SamsStatus")
    except dbus.DBusException:
        traceback.print_exc()
        print usage
        sys.exit(1)

    # create an interface wrapper for the remote object
    iface = dbus.Interface(remote_object, 'gov.pims.SamsService')

    # get status
    verbose = False
    sams_status = iface.show_status(verbose)
    print sams_status
    
    ## D-Bus exceptions are mapped to Python exceptions
    #try:
    #    iface.RaiseException()
    #except dbus.DBusException, e:
    #    print str(e)

    ## introspection is automatically supported
    #print remote_object.Introspect(dbus_interface="org.freedesktop.DBus.Introspectable")

    if 'stop' == sys.argv[1]:
        iface.Exit()

if __name__ == '__main__':
    main()

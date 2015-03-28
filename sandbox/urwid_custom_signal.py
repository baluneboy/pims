#!/usr/bin/env python

import urwid
import urwid.signals
import numpy as np

class Sig (object):
    __metaclass__ = urwid.signals.MetaSignals
    signals = ['custom']

    def send_signal(self):
        urwid.emit_signal(self, 'custom')

def main():

    txt = urwid.Text("Hello World")
    fill = urwid.Filler(txt, 'top')
    sig = Sig()

    def update():
        """Callback once the signal is received"""
        random_reset_sec = int( np.random.random() * 10 )
        fill.body = urwid.Text("Text Updated (reset in %ds)" % random_reset_sec)
        loop.set_alarm_in(random_reset_sec, reset_text, user_data=random_reset_sec)

    def reset_text(main_loop_obj, user_data):
        fill.body = urwid.Text("Back to hello with user data = " + '%d' % user_data)

    def show_or_exit(input):
        if input in ('q', 'Q'):
            raise urwid.ExitMainLoop()
        #We press the 'u' letter (as in update)
        if input is 'u':
            sig.send_signal()

    #connection between the object, the signal name and the callback
    urwid.connect_signal(sig, 'custom', update)
    loop = urwid.MainLoop(fill, unhandled_input=show_or_exit)
    loop.run()

if __name__ == '__main__':
    main()
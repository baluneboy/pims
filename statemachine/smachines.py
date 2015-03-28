#!/usr/bin/python

from smachine import StateMachine
from blinkstick import blinkstick

# Globals
access_code = "change this to AccessCode from BlinkStick.com"
bstick = blinkstick.find_first()
if bstick is None:
    sys.exit("BlinkStick not found...")

# a state machine for blinkstick pending real-time
class BlinkstickStateMachine(StateMachine):
    """a state machine for blinkstick pending real-time"""
    state = None
    states = ['pending', 'info', 'warning', 'critical']
    transitions = {
        None:       ['pending'],
        'pending':  ['info', 'warning', 'critical'],
        'info':     ['pending'],
        'warning':  ['pending'],
        'critical': ['pending'],
    }

    def __init__(self):
        self.pending() # start with pending

    def squawk(self, msg):
        print '%s: %s' % (self.__class__.__name__, msg)

    def on_enter_pending(self, from_state=None, to_state=None):
        if from_state == None:
            # initial entry point
            self.squawk( 'initial entry point, start pending' )
            return True
        elif from_state == 'info':
            self.squawk( 'from info, back to pending' )
            return True
        elif from_state == 'warning':
            self.squawk( 'from warning, back to pending' )
            return True
        elif from_state == 'critical':
            self.squawk( 'from critical, back to pending' )
            return True        
        else:
            return False

    def on_enter_info(self, from_state=None, to_state=None):
        if from_state == 'pending':
            # ready with processed info
            self.squawk( 'ready with processed info' )
            return True
        else:
            return False

    def on_enter_warning(self, from_state=None, to_state=None):
        if from_state == 'pending':
            # now need warning
            self.squawk( 'we got a warning' )
            return True
        else:
            return False

    def on_enter_critical(self, from_state=None, to_state=None):
        if from_state == 'pending':
            # now need critical
            self.squawk( 'THIS IS CRITICAL' )
            return True
        else:
            return False

# a state machine for plot parameters
class PlotParametersStateMachine(StateMachine):
    state = None
    states = ['monitor', 'found', 'pending', 'deployed', 'problem']
    transitions = {
        None:       ['monitor'],
        'monitor':  ['found'],
        'found':    ['pending'],
        'pending':  ['deployed', 'problem'],
        'deployed': ['monitor'],
        'problem':  ['monitor'],
    }

    def __init__(self):
        self.monitor() # start with monitor

    def squawk(self, msg):
        print '%s: %s' % (self.__class__.__name__, msg)

    def on_enter_monitor(self, from_state=None, to_state=None):
        if from_state == None:
            # initial entry point
            self.squawk( 'initial entry point, start monitoring' )
            return True
        elif from_state == 'problem':
            self.squawk( 'reset after problem, restart monitoring' )
            return True
        elif from_state == 'deployed':
            self.squawk( 'done with previous deployment, start monitoring' )
            return True
        else:
            return False

    def on_enter_found(self, from_state=None, to_state=None):
        if from_state == 'monitor':
            # found a file to be processed
            self.squawk( 'a file to be processed was found' )
            return True
        else:
            return False

    def on_enter_pending(self, from_state=None, to_state=None):
        if from_state == 'found':
            # now do processing
            self.squawk( 'file being processed, deployment still pending' )
            return True
        else:
            return False

    def on_enter_problem(self, from_state=None, to_state=None, msg=None):
        if from_state == 'pending':
            if msg:
                self.squawk( 'problem: %s' %  msg )
            return True
        else:
            return False

    def on_enter_deployed(self, from_state=None, to_state=None):
        if from_state == 'pending':
            # we done did it
            self.squawk( 'new file was deployed' )
            return True
        else:
            return False

def demo_plotparams():
    
    # create machine to maintain state info
    machine = PlotParametersStateMachine()
    
    # a bad sequence
    sequence = ['found', 'pending']
    for s in sequence:
        machine.push(s)
        machine.next()
    machine.problem('a big issue')

    # a good sequence
    sequence = ['monitor', 'found', 'pending', 'deployed', 'monitor']
    for s in sequence:
        machine.push(s)
        machine.next()
        
def demo_bstick():
    
    # create machine to maintain state info
    machine = BlinkstickStateMachine()

    # a good sequence (default initial state is pending)
    sequence = ['info', 'pending', 'warning', 'pending', 'critical']
    for s in sequence:
        machine.push(s)
        machine.next()
        
if __name__ == "__main__":
    demo_bstick()

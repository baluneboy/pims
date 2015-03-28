#!/usr/bin/python

import unittest
from smachine import StateException
from pims.statemachine.smachines import PlotParametersStateMachine
from pims.statemachine.smachines import BlinkstickStateMachine

class TestRealtimeBlinkstickStateMachine(unittest.TestCase):

    def test_state_transitions(self):

        # create machine to maintain state info
        machine = BlinkstickStateMachine()

        # test initial state
        self.assertEqual('pending', machine.state)

        # change state from pending to info returns True
        self.assertTrue( machine.info() )

        # verify state is now info
        self.assertEqual('info', machine.state)

        # change state from info to pending returns True
        self.assertTrue( machine.pending() )

        # verify state is now pending
        self.assertEqual('pending', machine.state)

        # change state from pending to warning returns True
        self.assertTrue( machine.warning() )

        # verify state is now warning
        self.assertEqual('warning', machine.state)

        # change state from warning to pending returns True
        self.assertTrue( machine.pending() )

        # verify state is now pending
        self.assertEqual('pending', machine.state)

        # change state from pending to info, then pending, then critical each returns True
        self.assertTrue( machine.info() )
        self.assertTrue( machine.pending() )
        self.assertTrue( machine.critical() )

        # change state from critical to pending returns True
        self.assertTrue( machine.pending() )

        # verify state is now pending
        self.assertEqual('pending', machine.state)
        self.assertRaises(StateException, machine.pending)

        # push state(s) into FIFO for "next" transition(s)
        machine.push('info')
        self.assertRaises(StateException, machine.push, 'warning')
        machine.push('pending')
        self.assertTrue(machine.next())
        self.assertTrue(machine.next())

        # change states to get back to pending via critical
        machine.critical()
        machine.pending()

class TestPlotParamStateMachine(unittest.TestCase):

    def test_state_transitions(self):

        # create machine to maintain state info
        machine = PlotParametersStateMachine()

        # test initial state
        self.assertEqual('monitor', machine.state)

        # change state from problem to found returns True
        self.assertTrue( machine.found() )

        # verify state is now found
        self.assertEqual('found', machine.state)

        # change state from found to pending returns True
        self.assertTrue( machine.pending() )

        # verify state is now pending
        self.assertEqual('pending', machine.state)

        # change state from pending to deployed returns True
        self.assertTrue( machine.deployed() )

        # verify state is now deployed
        self.assertEqual('deployed', machine.state)

        # change state from deployed to monitor returns True
        self.assertTrue( machine.monitor() )

        # verify state is now monitor
        self.assertEqual('monitor', machine.state)

        # change state from monitor to found, then pending, then problem each returns True
        self.assertTrue( machine.found() )
        self.assertTrue( machine.pending() )
        #self.assertTrue( machine.problem(msg='could not deploy parameters') )
        self.assertTrue( machine.problem() )

        # change state from problem to monitor returns True
        self.assertTrue( machine.monitor() )

        # verify state is now monitor
        self.assertEqual('monitor', machine.state)
        self.assertRaises(StateException, machine.problem)

        # push state(s) into FIFO for "next" transition(s)
        machine.push('found')
        self.assertRaises(StateException, machine.push, 'deployed')
        machine.push('pending')
        self.assertTrue(machine.next())
        self.assertTrue(machine.next())

        # change states to get back to monitor via problem
        machine.problem()
        machine.monitor()

def plot_params_suite():
    return unittest.makeSuite(TestPlotParamStateMachine, 'test')

def blinkstick_realtime_suite():
    return unittest.makeSuite(TestRealtimeBlinkstickStateMachine, 'test')

if __name__ == '__main__':
    #unittest.main(defaultTest='plot_params_suite')
    unittest.main(defaultTest='blinkstick_realtime_suite')

#!/usr/bin/python
from smachine import StateMachine, StateException

try:
    import unittest2 as unittest
except ImportError:
    import unittest
    
class TestMachine(StateMachine):
    states = ['green', 'yellow', 'red']
    transitions = {
        'green': ['yellow', 'red'],
        'yellow': ['green', 'red'],
        'red': ['yellow']
    }
    
    def __init__(self):
        self.state = 'green'
    
    def on_enter_red(self, from_state=None, to_state=None):
        if from_state == 'green':
            return False

class TestStateMachine(unittest.TestCase):
    def test_state_transitions(self):
        machine = TestMachine()
        self.assertFalse(machine.red())
        self.assertEqual('green', machine.state)
        self.assertTrue(machine.yellow())
        self.assertEqual('yellow', machine.state)
        self.assertTrue(machine.red())
        self.assertEqual('red', machine.state)
        self.assertRaises(StateException, machine.green)
        self.assertTrue(machine.yellow())
        self.assertEqual('yellow', machine.state)
        self.assertTrue(machine.green())
        self.assertEqual('green', machine.state)
        
        machine.push('yellow')
        machine.push('red')
        
        self.assertRaises(StateException, machine.push, 'green')
        
        self.assertTrue(machine.next())
        self.assertTrue(machine.next())
        
        self.assertRaises(StateException, machine.push, 'green')
        
        machine.yellow()
        machine.green()

def suite():
    return unittest.makeSuite(TestStateMachine, 'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
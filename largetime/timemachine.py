#!/usr/bin/env python

import datetime
from nose.tools import assert_true, assert_false
from statemachine import event, Machine, transition_to, transition_from

DEBUG = True

def debug_print(s):
    if DEBUG: print s

# a 5-state machine for db timestamp conditions (fresh, stale, morestale, moststale, rotten)
class TimeMachine(Machine):
    initial_state, color, time = 'rotten', 'red', None

    # these are for asserting things
    became_rotten = False
    left_rotten = False

    # when we change the default timing of transition_from/transition_to, we
    # want to ensure that we were triggerd at the right time
    was_fresh_when_becoming_rotten = False
    went_stale_when_leaving_rotten = False

    def __init__(self, table, expected_delta_sec=0.9, host='manbearpig'):
        super(TimeMachine, self).__init__()
        self.table = table
        self.expected_delta_sec = expected_delta_sec
        self.host = host

    def __str__(self):
        if self.time:
            timestr = self.time.strftime('%H:%M:%S')
        else:
            timestr = 'HH:MM:SS'
        return 'now the time is %s (%s, %s) [%s on %s]' % (
            timestr, self.state, self.color, self.table, self.host)

    def get_db_time(self):
        # FIXME with "rt" db table query on host
        return datetime.datetime.now()

    def update(self):
        old_time = self.time
        new_time = self.get_db_time()
        if not new_time:
            self.time = None
            self.go_rotten()
            return
        if not old_time:
            self.time = new_time
            self.go_fresh()
            return
        self.time = new_time
        delta_sec = (new_time - old_time).total_seconds()
        if delta_sec >= self.expected_delta_sec:
            self.more_fresh()
            return
        else:
            self.less_fresh()
            return

    @event
    def go_rotten(self):
        debug_print(' go rotten')
        yield ('fresh', 'stale', 'morestale', 'moststale'), 'rotten'

    @event
    def less_fresh(self):
        debug_print(' go less fresh')
        yield 'fresh', 'stale'
        yield 'stale', 'morestale'
        yield 'morestale', 'moststale'
        yield 'moststale', 'rotten'

    @event
    def more_fresh(self):
        debug_print(' go MORE fresh')
        yield 'rotten', 'moststale'
        yield 'moststale', 'morestale'
        yield 'morestale', 'stale'
        yield 'stale', 'fresh'

    @event
    def go_fresh(self):
        debug_print(' go to fresh')
        yield ('fresh', 'stale', 'morestale', 'moststale', 'rotten'), 'fresh'

    @transition_to('fresh')
    def becoming_fresh(self):
        # do something, then last 2 lines are:
        self.color = 'white'
        debug_print('    > transitioned to fresh')
        self.became_fresh = True

    @transition_to('stale')
    def becoming_stale(self):
        # do something, then last 2 lines are:
        self.color = 'yellow'
        debug_print('    > transitioned to stale')
        self.became_stale = True

    @transition_to('rotten')
    def becoming_rotten(self):
        # do something, then last 2 lines are:
        self.color = 'red'
        debug_print('    > transitioned to rotten')
        self.became_rotten = True
        self.left_rotten = False

    @transition_from('rotten')
    def leaving_rotten(self):
        debug_print('  transitioned from rotten')
        # do something and last line is:
        self.left_rotten = True
        self.became_rotten = False

    @transition_to('rotten', 'before')
    def before_becoming_rotten(self):
        debug_print('  (%s) before transition to rotten' % self.state)
        self.was_fresh_when_becoming_rotten = self.state == 'fresh'

    @transition_from('rotten', 'after')
    def after_leaving_rotten(self):
        debug_print('  after transition from rotten (%s)' % self.state)
        self.went_stale_when_leaving_rotten = self.state == 'stale'

def demo():
    tm = TimeMachine('es05', host='manbearpig')
    print tm
    for i in range(4):
        tm.more_fresh()
        print i, tm
    for i in range(3):
        tm.less_fresh()
        print i, tm
    tm.go_fresh()
    print tm
    tm.go_rotten()
    print tm
    tm.go_rotten()
    print tm

demo()
raise SystemExit

def test_transition_to():
    m = TimeMachine('es05')
    assert_true(m.state=='rotten') # test initial state

    m.go_fresh()
    assert_true(m.state=='fresh')
    assert_true(m.color=='white')

    m.go_rotten()
    assert_true(m.state=='rotten')
    assert_true(m.color=='red')    
    
    m.go_fresh()
    m.less_fresh()
    assert_true(m.state=='stale')
    m.less_fresh()
    assert_true(m.state=='rotten')    

def test_transition_from():
    m = TimeMachine('es06', 'localhost')
    assert_false(m.left_rotten)
    assert_false(m.went_stale_when_leaving_rotten)

    m.go_fresh()
    assert_true(m.left_rotten)
    assert_false(m.went_stale_when_leaving_rotten)

    m.go_rotten()
    assert_true(m.was_fresh_when_becoming_rotten)
    assert_true(m.became_rotten)
    assert_false(m.left_rotten)
    m.update() # goes from rotten straight to fresh
    assert_true(m.state=='fresh')
    assert_true(m.left_rotten)
    assert_false(m.became_rotten)
    
    m.go_rotten()
    m.more_fresh()
    assert_true(m.went_stale_when_leaving_rotten)

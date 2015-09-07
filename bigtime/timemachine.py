#!/usr/bin/env python

import time
import datetime
from itertools import cycle
from collections import deque
from nose.tools import assert_true, assert_false
from statemachine import event, Machine, transition_to, transition_from
from onerowquery import query_onerow_unixtime, table_exists, query_timestamp, query_ku_timestamp, query_hirap

from pims.utils.pimsdateutil import unix2dtm
from pims.utils.pimsdateutil import dtm2unix

DEBUG = 0

def debug_print(s):
    if DEBUG: print s

# get real-time db table unix time (like from es05rt table)
class TimeGetter(object):
    """get real-time db table unix time (like from es05rt table)"""
    
    def __init__(self, table, host='manbearpig'):
        self.table = table
        self.host = host
        if table_exists(self.table, self.host):
            self._get_time_func = self._get_time
        else:
            self._get_time_func = lambda : None

    def get_time(self):
        return self._get_time_func() # time func resolved during init
    
    def _get_time(self):
        return query_onerow_unixtime(self.table, host=self.host)

class HirapTimeGetter(TimeGetter):
    
    def _get_time(self):
        return query_hirap(self.table, host=self.host)

# get yoda samsmon db ee_packet table timestamp
class EeTimeGetter(TimeGetter):
    """get yoda samsmon db ee_packet table timestamp"""

    def __init__(self, *args, **kwargs):
        self.ee_id = kwargs.pop('ee_id')
        super(EeTimeGetter, self).__init__(*args, **kwargs)

    def _get_time(self):
        return query_timestamp(self.ee_id, self.table, host=self.host)    

# get yoda samsmon db gse_packet table latest ku_timestamp
class KuTimeGetter(TimeGetter):
    """get yoda samsmon db gse_packet table latest ku_timestamp"""

    def _get_time(self):
        return query_ku_timestamp(self.table, host=self.host) 

# dummy unix time getter that utiliizes sequence of deltas (sec) via generator
class RapidTimeGetter(TimeGetter):
    """dummy unix time getter that utiliizes sequence of deltas (sec) via generator"""
    
    def __init__(self, *args, **kwargs):
        if 'shift' in kwargs:
            self.shift = kwargs.pop('shift')
        else:
            self.shift = 0
        super(RapidTimeGetter, self).__init__(*args, **kwargs)
        self._init_time = dtm2unix(datetime.datetime(2015,1,1))
        deltas = deque([ None, None, None, 0, 1, 2, 3, 3, 3, 4, 5, 6, 4, 4, 4, 5 ])
        deltas.rotate(self.shift)
        self._pool = cycle(deltas)
    
    def get_time(self):
        time.sleep(0.25)
        delta = self._pool.next()
        if delta is None:
            return None
        return self._init_time + delta

# a 3-state machine for db unix times (fresh, stale, rotten)
class TimeMachine(Machine):
    """a 3-state machine for db unix times (fresh, stale, rotten)"""
    
    initial_state, color, time = 'rotten', 'red', None

    # these are for asserting things
    became_rotten, left_rotten = False, False
    became_stale,  left_stale  = False, False
    became_fresh,  left_fresh  = False, False

    # when we change the default timing of transition_from/transition_to, we
    # want to ensure that we were triggerd at the right time
    was_stale_when_becoming_rotten = False
    went_stale_when_leaving_rotten = False

    def __init__(self, time_getter, expected_delta_sec=0.9):
        super(TimeMachine, self).__init__()
        self.time_getter = time_getter
        self.expected_delta_sec = expected_delta_sec

    def __str__(self):
        if self.time:
            timestr = unix2dtm(self.time).strftime('%H:%M:%S')
        else:
            timestr = 'HH:MM:SS'
        #return 'now the time is %s (%s, %s)' % (timestr, self.state, self.color)
        return 'now the time is %s (%s, %s)' % (self.time, self.state, self.color)        

    def update(self):
        old_time = self.time
        new_time = self.time_getter.get_time()
        self.time = new_time
        if not new_time:
            self.less_fresh()
            return
        if not old_time:
            self.more_fresh()
            return
        delta_sec = new_time - old_time
        #print self.time_getter.table, delta_sec
        if delta_sec >= self.expected_delta_sec:
            self.more_fresh()
        else:
            self.less_fresh()

    @event
    def less_fresh(self):
        debug_print(' go less fresh')
        yield 'fresh', 'stale'
        yield 'stale', 'rotten'

    @event
    def more_fresh(self):
        debug_print(' go MORE fresh')
        yield 'rotten', 'stale'
        yield 'stale', 'fresh'

    ###############################
    # FRESH TRANSITIONS

    @transition_to('fresh')
    def becoming_fresh(self):
        # do something
        self.color = 'white'
        debug_print('    > transitioned to fresh')
        self.became_fresh = True
        self.left_fresh = False

    @transition_from('fresh')
    def leaving_fresh(self):
        debug_print('  transitioned from fresh')
        # do something
        self.became_fresh = False
        self.left_fresh = True

    ###############################
    # STALE TRANSITIONS

    @transition_to('stale')
    def becoming_stale(self):
        # FIXME had to change color from yellow to white due to es06 white/yellow flicker
        #self.color = 'yellow'
        self.color = 'white'
        debug_print('    > transitioned to stale')
        self.became_stale = True
        self.left_stale = False

    @transition_from('stale')
    def leaving_stale(self):
        debug_print('  transitioned from stale')
        # do something
        self.became_stale = False
        self.left_stale = True

    ###############################
    # ROTTEN TRANSITIONS

    @transition_to('rotten')
    def becoming_rotten(self):
        # do something
        self.color = 'red'
        debug_print('    > transitioned to rotten')
        self.became_rotten = True
        self.left_rotten = False

    @transition_from('rotten')
    def leaving_rotten(self):
        debug_print('  transitioned from rotten')
        # do something
        self.became_rotten = False
        self.left_rotten = True

    @transition_to('rotten', 'before')
    def before_becoming_rotten(self):
        debug_print('  (%s) before transition to rotten' % self.state)
        self.was_stale_when_becoming_rotten = self.state == 'stale'

    @transition_from('rotten', 'after')
    def after_leaving_rotten(self):
        debug_print('  after transition from rotten (%s)' % self.state)
        self.went_stale_when_leaving_rotten = self.state == 'stale'

class LargeTimeMachine(TimeMachine):
    rect_color = None
    
    @transition_to('rotten', 'before')    
    def before_becoming_rotten(self):
        super(LargeTimeMachine, self).before_becoming_rotten()        
        debug_print('  oh boy, here we are again')

    # TODO find out why we do not include @event decorator here
    def less_fresh(self):
        super(LargeTimeMachine, self).less_fresh()
        debug_print(' AND I MEAN BIG TIME')
    
def test_transition_to():
    tg = RapidTimeGetter(None, host=None)
    m = TimeMachine(tg)
    assert_true(m.state=='rotten') # initially rotten
    assert_true(m.color=='red')
    
    m.more_fresh() # now stale
    assert_true(m.state=='stale')
    assert_true(m.color=='yellow')
    assert_true(m.left_rotten)
    assert_true(m.became_stale)
    
    m.more_fresh() # now fresh
    assert_true(m.state=='fresh')
    assert_true(m.color=='white')
    assert_true(m.left_rotten)
    assert_true(m.became_fresh)
    
    m.more_fresh() # still fresh
    assert_true(m.state=='fresh')
    assert_true(m.color=='white')
    assert_false(m.left_fresh)
    assert_true(m.became_fresh)    
    
    m.less_fresh() # now stale
    assert_true(m.state=='stale')
    assert_true(m.color=='yellow')
    assert_true(m.left_fresh)
    assert_true(m.became_stale)       
    
    m.less_fresh() # now rotten
    assert_true(m.state=='rotten')
    assert_true(m.color=='red')
    assert_true(m.became_rotten)
    assert_true(m.left_stale)
    
    m.less_fresh() # still rotten
    assert_true(m.state=='rotten')    
    assert_true(m.color=='red')
    assert_false(m.left_rotten)
    assert_true(m.became_rotten)
    
def test_transition_from():
    tg = RapidTimeGetter(None, host=None)
    m = TimeMachine(tg)
    assert_false(m.left_rotten)
    assert_false(m.went_stale_when_leaving_rotten)

    m.more_fresh() # now stale
    assert_true(m.left_rotten)
    assert_true(m.went_stale_when_leaving_rotten)

    m.less_fresh() # now rotten
    assert_true(m.was_stale_when_becoming_rotten)
    
    m.less_fresh() # still rotten

    assert_true(m.became_rotten)
    assert_false(m.left_rotten)
    
    #m.update() # goes from rotten straight to fresh
    
    assert_true(m.state=='rotten')

def test_transitions():
    tg = RapidTimeGetter(None, host=None)
    m = TimeMachine(tg)
    assert_false(m.left_rotten)
    assert_false(m.went_stale_when_leaving_rotten)

    m.more_fresh() # now stale
    assert_true(m.left_rotten)
    assert_true(m.went_stale_when_leaving_rotten)    

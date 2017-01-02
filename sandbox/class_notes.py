#!/usr/bin/env python

class Car(object):

    wheels = 4

    # static (class-level) methods do not get first, "self", arg
    @staticmethod
    def make_car_sound():
        print 'VRooooommmm!'
        
    def __init__(self, make, model):
        self.make = make
        self.model = model

class SomeClass(object):
    
    def __init__(self, x):
        self._x = x

    @property
    def x(self):
        return self._x

    def _get_x(self):
        print 'getting x'
        return self._x

    def _set_x(self, val):
        print 'setting x to', val
        self._x = val
        
    x = property(_get_x, _set_x)

def print_debug(s):
    if 'DEBUGGING' in globals():
        _debug = DEBUGGING
    else:
        _debug = False
    if _debug: print (s)
        
class Celsius(object):
    
    def __init__(self, temperature = 0.0):
        self.temperature = temperature

    def to_fahrenheit(self):
        return (self.temperature * 1.8) + 32

    @property
    def temperature(self):
        print_debug("Getting value")
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        float_value = float(value)
        if float_value < -273.0:
            raise ValueError("temperature < -273 is not possible")        
        print_debug("Setting value")
        self._temperature = float_value

DEBUGGING = True
tc = Celsius('30')
DEBUGGING = False
print tc.temperature
tc.temperature -= 1
raise SystemExit

mustang = Car('Ford', 'Mustang')
print mustang.wheels
# 4
print Car.wheels

Car.make_car_sound()
mustang.make_car_sound()

sc = SomeClass('twist')
print sc.x
for x in [1, 'two', dict()]:
    sc._set_x(x)
    print sc.x

#!/usr/bin/env python

import pickle
import PyEcho
import datetime
import time
import RPi.GPIO as gpio

import pims.wemocontrol.wemo_backend as wemo_backend
from pims.echo.myring import retrieve, SECRETSDB_FILE

# FIXME get rid of unused imports

# FIXME document steps needed for secret file

def wemo_action(wemo, action):
   if wemo == "sendall":
      if action == "on":
          wemo_backend.sendall("on",wemo_backend.wemo_dict)
      elif action == "off":
          wemo_backend.sendall("off",wemo_backend.wemo_dict)
      elif action == "toggle":
          wemo_backend.sendall("toggle",wemo_backend.wemo_dict)
   elif action == "on":
      wemo_backend.wemo_dict[wemo].on()
   elif action == "off":
      wemo_backend.wemo_dict[wemo].off()
   elif action == "toggle":
      wemo_backend.wemo_dict[wemo].toggle()
   elif action == "update":
      wemo_backend.wemo_dict[wemo].update()
   elif action == "read":
      wemo_backend.wemo_dict[wemo].read(1)

def open_the_garage():
   PIN_OUT = 17

   gpio.setmode(gpio.BCM)
   gpio.setup(PIN_OUT, gpio.OUT)

   gpio.output(PIN_OUT, True)
   time.sleep(0.9)
   gpio.output(PIN_OUT, False)

   gpio.cleanup()

def blink_the_lights():
   for dev in ['lamp', 'sweat']:
      for a in ['on', 'off', 'on', 'off']:
         time.sleep(0.35)
         wemo_action(dev, a)

def go_to_work():
   open_the_garage()
   blink_the_lights()
   #turn_off_condo()

# Load or create secrets database:
with open(SECRETSDB_FILE) as f:
    db = pickle.load(f)
if db == {}: raise IOError

### Initialize ###
uname = retrieve('username')
pword = retrieve('password7')
print 'done initializing'

# Create an echo object
echo = PyEcho.PyEcho(uname, pword)

# Listen for events.
# FIXME This is naive, it assumes the above worked.
while True:
   # Fetch our tasks
   tasks = echo.tasks()

   # Process each one
   for task in tasks:

      # Do something depending on the task here.
      # FIXME this should be much better parsing than just startswith
      print "New task found: " + task['text']
      if task['text'].startswith('open the garage'):
         open_the_garage()
      elif task['text'].startswith('blink the lights'):
         blink_the_lights()
      elif task['text'].startswith('blank the lights'):
         blink_the_lights()
      elif task['text'].startswith('go to work'):
         go_to_work()

      # Now that we're done with it, delete it.
      # FIXME Again, this is naive. We should error check the response code.
      echo.deleteTask(task)

   # Wait 11 seconds and do it again
   print datetime.datetime.now()
   time.sleep(11)

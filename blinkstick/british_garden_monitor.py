#!/usr/bin/env python

# TODO get pibow case
# TODO uWSGI
# Wireless Network Camera

from flask import Flask
from blinkstick import blinkstick

app = Flask(__name__)
bsticks = blinkstick.find_all()

@app.route('/')
def home():
    for bstick in blinksticks:
        bstick.pulse_color(255, 0, 0)
        bstick.pulse_color(255, 255, 0)
    return 'redyellow'

if __name__ == "__main__":
    app.run(host='0.0.0.0')

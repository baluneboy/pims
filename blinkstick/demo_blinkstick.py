#!/usr/bin/env python

import time
import websocket
import json
import sys
from blinkstick import blinkstick

access_code = "change this to AccessCode from BlinkStick.com"

bstick = blinkstick.find_first()

if bstick is None:
    sys.exit("BlinkStick not found...")

def HTMLColorToRGB(colorstring):
    """ convert #RRGGBB to an (R, G, B) tuple """
    colorstring = colorstring.strip()
    if colorstring[0] == '#': colorstring = colorstring[1:]
    if len(colorstring) != 6:
        raise ValueError, "input #%s is not in #RRGGBB format" % colorstring
    r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:]
    r, g, b = [int(n, 16) for n in (r, g, b)]
    return (r, g, b)

def on_message(ws, message):
    global client_id
    global access_code
    global bstick

    #Uncomment this for debugging purposes
    #print message

    m = json.loads(message)

    if m[0]['channel'] == '/meta/connect':
        ws.send(json.dumps(
            {'channel': '/meta/connect',
             'clientId': client_id,
             'connectionType': 'websocket'}))
        return

    elif m[0]['channel'] == '/meta/handshake':
        client_id = m[0]['clientId']

        print "Acquired clientId: " + client_id

        ws.send(json.dumps(
            {'channel': '/meta/subscribe',
             'clientId': client_id,
             'subscription': '/devices/' + access_code}))
        return

    elif m[0]['channel'] == '/devices/' + access_code:
        if 'color' in m[0]["data"]:
            print "Received color: " + m[0]["data"]["color"]

            (r, g, b) = HTMLColorToRGB(m[0]["data"]["color"])
            bstick.set_color(r, g, b)
        elif 'status' in m[0]["data"] and m[0]["data"]['status'] == "off":
            print "Turn off"
            bstick.turn_off()

    elif m[0]['channel'] == '/meta/subscribe':
        if m[0]['successful']:
            print "Subscribed to device. Waiting for color message..."
        else:
            print "Subscription to the device failed. Please check the access_code value in the file."

    #Reconnect again and wait for further messages
    ws.send(json.dumps(
        {'channel': '/meta/connect',
         'clientId': client_id,
         'connectionType': 'websocket'}))

def on_error(ws, error):
    print error

def on_close(ws):
    print "### closed ###"

def on_open(ws):
    ws.send(json.dumps(
        {'channel': '/meta/handshake',
         'version': '1.0',
         'supportedConnectionTypes': ['long-polling', 'websocket']}))

def demo_web():
    # Set this to True for debugging purposes
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp("ws://live.blinkstick.com:9292/faye",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()    

def demo_set_get_block_info(info_block1, info_block2):
    
    bstick = blinkstick.find_first()
    
    # set and get device info-block1 here
    bstick.set_info_block1(info_block1)
    print bstick.get_info_block1()
    
    # set and get device info-block2 here
    bstick.set_info_block2(info_block2)
    print bstick.get_info_block2()
    
if __name__ == "__main__":
    #bstick.set_random_color(); time.sleep(2); bstick.turn_off(); raise SystemExit
    demo_set_get_block_info("abcdefghijklmnopqrstuvwxyz", "ABCDEFGHIJKLMNOPQRSTUVWXYZ")

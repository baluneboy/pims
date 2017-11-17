#!/usr/bin/env python

import cv2
#from numpy import *
import numpy as np

test_imgs = ['night_open.jpg', 'night_closed.jpg', 'day_open.jpg', 'day_closed.jpg']

for imgFile in test_imgs:
    img = cv2.imread('/Users/ken/Pictures/' + imgFile)
    height, width, channels = img.shape
    mask = np.zeros((height+2, width+2), np.uint8)

    # the starting pixel for the floodFill
    start_pixel = (510,110)
    
    # maximum distance to start pixel:
    diff = (2, 2, 2)

    retval, im, ma, rect = cv2.floodFill(img, mask, start_pixel, (0,255,0), diff, diff)

    print retval

    # check the size of the floodfilled area, if its large the door is closed:
    if retval > 10000:
        print imgFile + ": garage door closed"
    else:
        print imgFile + ": garage door open"

    cv2.imwrite(imgFile.replace(".jpg", "") + "_result.jpg", img)
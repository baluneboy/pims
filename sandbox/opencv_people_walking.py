#!/usr/bin/env python

import numpy as np
import cv2

#cap = cv2.VideoCapture('/Users/ken/Pictures/people-walking.mp4')
cap = cv2.VideoCapture('/Users/ken/Pictures/garage_take001.mp4')
fgbg = cv2.createBackgroundSubtractorMOG2()

while(1):
    try:
        ret, frame = cap.read()
        if ret == True:
            fgmask = fgbg.apply(frame)
            #cv2.imshow('fgmask', frame)
            cv2.imshow('frame', fgmask)
            k = cv2.waitKey(30) & 0xff
            if k == 27:
                break
            
        else:
            print 'video must be done'
            break

        
    except Exception, e:
        print 'oops'
        break

cap.release()
cv2.destroyAllWindows()

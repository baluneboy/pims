#!/usr/bin/env python

import numpy as np
import cv2
from matplotlib import pyplot as plt

img = cv2.imread('/tmp/simple.jpg',0)
imgOut = img.copy()
imgFast = img.copy()

# Initiate FAST object with default values
fast = cv2.FastFeatureDetector_create()

# find and draw the keypoints
kp = fast.detect(img,None)
img2 = cv2.drawKeypoints(img, kp, imgOut, color=(255,0,0))

# Print all default params
print "Threshold: ", fast.getThreshold()
print "nonmaxSuppression: ", fast.getNonmaxSuppression()
print "neighborhood: ", fast.getType()
print "Total Keypoints with nonmaxSuppression: ", len(kp)

cv2.imwrite('/tmp/fast_true.png',img2)  # WITH nonmaxSuppression

# Disable nonmaxSuppression
fast.setNonmaxSuppression(0)
kp = fast.detect(img,None)

print "Total Keypoints without nonmaxSuppression: ", len(kp)

img3 = cv2.drawKeypoints(img, kp, imgFast, color=(255,0,0))

cv2.imwrite('/tmp/fast_false.png', img3)  # WITHOUT nonmaxSuppression

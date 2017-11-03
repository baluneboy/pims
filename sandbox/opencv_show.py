#!/usr/bin/env python

import sys
import cv2
from opencv_survey import disp_save_img

image_fname = sys.argv[1]
img = cv2.imread(image_fname)
disp_save_img(img)

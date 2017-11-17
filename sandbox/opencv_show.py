#!/usr/bin/env python

import sys
import cv2
from opencv_survey import disp_save_img

image_fname = sys.argv[1]
img = cv2.imread(image_fname)


#x, y = 608, 240
#roi = img[y:y+100, x:x+200]
#cv2.GaussianBlur(roi, (9, 9), 0)

# for starters just copy a roi to another part of the image
x, y = 608, 240
d = 50
roi = img[y-d:y+d, x-d:x+d]
img[200:200+(2*d), 100:100+(2*d)] = roi

disp_save_img(img)

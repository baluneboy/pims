#!/usr/bin/env python

import os
import cv2
import numpy as np
from opencv_survey import disp_save_img


def orb_feature_matching(img1, img2):
    """match img2 to template of img1 using ORB"""

    orb = cv2.ORB_create()
    
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)
    
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    
    matches = bf.match(des1, des2)
    matches = sorted(matches, key = lambda x:x.distance)
    
    img3 = cv2.drawMatches(img1, kp1, img2, kp2, matches[:10], None, flags=2)

    disp_save_img(img3)


def test_the_orb():
    img1 = cv2.imread('/Users/ken/Pictures/garage_template.jpg',0)
    img2 = cv2.imread('/Users/ken/Pictures/garage.jpg',0)
    #orb_feature_matching(img1, img2)
    disp_save_img(img2)


#test_imgs = ['night_open.jpg', 'night_closed.jpg', 'day_open.jpg', 'day_closed.jpg']
test_imgs = [
    #'2017-11-04_14_38_open.jpg', '2017-11-04_14_38_close.jpg',
    #'2017-11-06_15_56_open.jpg', '2017-11-06_15_56_close.jpg',
    #'2017-11-07_15_53_open.jpg', '2017-11-07_15_53_close.jpg',
    #'2017-11-08_18_44_open.jpg', '2017-11-08_18_44_close.jpg',
     '2017-11-10_12_30_open.jpg', '2017-11-10_12_30_close.jpg',
    ]

for bname in test_imgs:
    image_fname = '/Users/ken/Pictures/foscam/' + bname
    #image_fname = '/home/ken/pictures/foscam/' + bname
    img = cv2.imread(image_fname)
    #print image_fname
    #print os.path.exists(image_fname)
    height, width, channels = img.shape
    mask = np.zeros((height+2, width+2), np.uint8)

    # FIXME derive starting pixel from template matching in case camera moves
    # the starting pixel for the floodFill
    start_pixel = (608, 240)
    
    # maximum distance to start pixel
    diff = (2, 2, 2)

    # use blurring to smooth the image a bit
    blur = cv2.GaussianBlur(img, (7, 7), 0)

    #retval, im, ma, rect = cv2.floodFill(img, mask, start_pixel, (0,255,0), diff, diff)
    retval, im, ma, rect = cv2.floodFill(blur, mask, start_pixel, (0,255,0), diff, diff)

    # check the size of the floodfilled area, if its large the door is closed:
    if retval > 555:
        print '%s: garage is closed ( %9d )' % (image_fname, retval)
    else:
        print '%s:  garage is opened ( %9d )' % (image_fname, retval)       

    #cv2.imwrite(image_fname.replace(".jpg", "") + "_result.jpg", img)
    cv2.imwrite(image_fname.replace(".jpg", "") + "_result.jpg", blur)
    
#image_fname = '/Users/ken/Pictures/foscam/2017-10-31_15_50_foscam.jpg'
#img = cv2.imread(image_fname)
#disp_save_img(img)

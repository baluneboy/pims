#!/usr/bin/env python

import cv2
import numpy as np
from matplotlib import pyplot as plt

# UL = (400, 27)
#
# GARAGE RECT
# ULG = (567, 181) => offset: (167, 154) +++ xywh: (167, 154, 52, 112)
# BRG = (619, 293) => offset: (219, 266)
#
# LIGHT-PAINTED RECT
# ULP = (603, 225) => offset: (203, 198) +++ xywh: (203, 198, 10, 34)
# BRP = (613, 259) => offset: (213, 232)
    
#OFFSETXY_WH = [ (167, 154, 52, 112), (203, 198, 10, 34) ]
OFFSETXY_WH = [ (203, 198, 10, 34) ]


def demo_general(show_result=False):

    #img = cv2.imread('/Users/ken/Pictures/foscam/2017-11-04_08_47_open.jpg', 0)
    img = cv2.imread('/home/ken/pictures/foscam/2017-11-04_08_47_open.jpg', 0)
    img2 = img.copy()
    #template = cv2.imread('/Users/ken/Pictures/foscam/template.jpg', 0)
    template = cv2.imread('/home/ken/pictures/foscam/template.jpg', 0)    
    w, h = template.shape[::-1]
    
    # All the 6 methods for comparison in a list
    methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED',
                'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']
    
    for meth in methods:
        img = img2.copy()
        method = eval(meth)
    
        # Apply template Matching
        res = cv2.matchTemplate(img, template, method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
        # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            top_left = min_loc
        else:
            top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)
    
        # draw rectangle around where template was found in target image
        cv2.rectangle(img, top_left, bottom_right, 255, 2)
        
        # FIXME the white-paint region gets clobbered by door opening's rectangle
        # draw 2 more filled rectangles around door opening and white-paint region
        for offsetxy_wh in OFFSETXY_WH:
            t = (top_left[0] + offsetxy_wh[0], top_left[1] + offsetxy_wh[1])
            b = (t[0] + offsetxy_wh[2], t[1] + offsetxy_wh[3])
            cv2.rectangle(img, t, b, 255, -2)

        print meth, top_left
        
        if show_result:
            plt.subplot(121),plt.imshow(res,cmap = 'gray')
            plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
            plt.subplot(122),plt.imshow(img,cmap = 'gray')
            plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
            plt.suptitle(meth)
            plt.show()


if __name__ == '__main__':
    
    import sys 
    show_result = eval(sys.argv[1])
    demo_general(show_result=show_result)

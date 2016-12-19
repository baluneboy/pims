#!/usr/bin/env python

import cv2
import numpy as np
import matplotlib.pyplot as plt


def load_img_gray(fname):
    return cv2.imread(fname, 0)


def disp_save_img(img):
    cv2.imshow('image', img)
    k = cv2.waitKey(0)
    if k == 1048603: # wait for ESC key
        print 'user hit ESC'
        cv2.destroyAllWindows()
    elif k == 1048691: # wait for 's' key to save and exit
        cv2.imwrite('/tmp/messy.jpg', img)
        print 'wrote /tmp/messy.jpg'
        cv2.destroyAllWindows()
    else:
        print 'unhandled key %d' % k


def matplot_img(img):
    # this gives us some utilities for free (like zoom, save, home)
    plt.imshow(img, cmap='gray', interpolation='bicubic')
    plt.xticks([]); plt.yticks([]); # hide ticks
    plt.show()


def draw_line(p1, p2):
    """draw line on black img from p1 to p2"""
    # create blank black image
    img = np.zeros((512, 512, 3), np.uint8)
    
    # draw line with thickness of 5px
    img = cv2.line(img, (0, 0), (511, 511), (255, 0, 0), 5)
    
    disp_save_img(img)
    

def affine_transformation(img):
    """seems sensitive to pts1 and pts2; output depends greatly on those"""    
    #img = cv2.imread(fname, 0)
    #rows,cols,ch = img.shape
    rows,cols = img.shape
    
    pts1 = np.float32([[50,50],[200,50],[50,200]])
    pts2 = np.float32([[10,100],[200,50],[100,250]])
    
    M = cv2.getAffineTransform(pts1,pts2)
    
    dst = cv2.warpAffine(img,M,(cols,rows))
    
    plt.subplot(121),plt.imshow(img),plt.title('Input')
    plt.subplot(122),plt.imshow(dst),plt.title('Output')
    plt.show()
    
    
def perspective_transformation(fname):
    """seems sensitive to pts1 and pts2; output depends greatly on those"""
    img = cv2.imread(fname)
    rows,cols,ch = img.shape
    
    pts1 = np.float32([[56,65],[368,52],[28,387],[389,390]])
    pts2 = np.float32([[0,0],[300,0],[0,300],[300,300]])
    
    M = cv2.getPerspectiveTransform(pts1,pts2)
    
    dst = cv2.warpPerspective(img,M,(300,300))
    
    plt.subplot(121),plt.imshow(img),plt.title('Input')
    plt.subplot(122),plt.imshow(dst),plt.title('Output')
    plt.show()    
    
    
if __name__ == "__main__":
    fname = '/home/pims/Pictures/quickcheckerboard.png'
    fname = '/home/pims/Downloads/pre-affine.png'
    fname = '/home/pims/Downloads/perspective.png'
    
    perspective_transformation(fname)
    raise SystemExit

    img = load_img_gray(fname)

    affine_transformation(img)
    raise SystemExit

    # draw line
    draw_line( (10, 10), (220, 220) )
    
    raise SystemExit
    
    # matplotlib to show image and it gives us some utilities too
    matplot_img(img)
    
    # use opencv to display and maybe save img (not utilities in image display window)
    disp_save_img(img)
    

    
    
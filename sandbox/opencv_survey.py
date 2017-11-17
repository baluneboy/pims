#!/usr/bin/env python

import cv2
import numpy as np
import matplotlib.pyplot as plt


def load_img_gray(fname):
    return cv2.imread(fname, 0)


def disp_save_img(img, tag=''):
    cv2.imshow(tag + ' Hit ESC to close, mouse wheel zoom, right-click for options', img)
    k = cv2.waitKey(0)
    #print k
    if k == 27:  # (linux ESC = 1048603?) wait for ESC key
        print 'user hit ESC'
        cv2.destroyAllWindows()
    elif k == 115:  # (linux S key = 1048691?) wait for 's' key to save and exit
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
    
    
def fast_corner_detection(fname):   
    img = cv2.imread(fname,0)
    
    # Initiate FAST object with default values
    fast = cv2.FastFeatureDetector_create()
    
    # find and draw the keypoints
    kp = fast.detect(img,None)
    img2 = cv2.drawKeypoints(img, kp, None, color=(255,0,0))
    
    # Print all default params
    print "Threshold: ", fast.getThreshold()
    print "nonmaxSuppression: ", fast.getNonmaxSuppression()
    print "neighborhood: ", fast.getType()
    print "Total Keypoints with nonmaxSuppression: ", len(kp)
    
    cv2.imwrite('/tmp/fast_true.png',img2)
    
    # Disable nonmaxSuppression
    fast.setNonmaxSuppression(0)
    kp = fast.detect(img,None)
    
    print "Total Keypoints without nonmaxSuppression: ", len(kp)
    
    img3 = cv2.drawKeypoints(img, kp, None, color=(255,0,0))
    
    cv2.imwrite('/tmp/fast_false.png',img3)
    
    
def track_good_features(fname):
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    gray = np.float32(gray)
    corners = cv2.goodFeaturesToTrack(gray, 100, 0.01, 10)
    corners = np.int0(corners)        
    for corner in corners:
        x,y = corner.ravel()
        cv2.circle(img,(x,y),3,255,-1)
        
    cv2.imshow('Corner',img)    
    
    
def demo_5bucks(fname):
    
    img = load_img_gray(fname)
    affine_transformation(img)
    
    # matplotlib to show image and it gives us some utilities too
    matplot_img(img)
    
    # use opencv to display and maybe save img (not utilities in image display window)
    disp_save_img(img)


def orb_feature_matching():
    img1 = cv2.imread('/Users/ken/Pictures/opencv-feature-matching-template.jpg',0)
    img2 = cv2.imread('/Users/ken/Pictures/opencv-feature-matching-image.jpg',0)

    orb = cv2.ORB_create()
    
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)
    
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    
    matches = bf.match(des1, des2)
    matches = sorted(matches, key = lambda x:x.distance)
    
    img3 = cv2.drawMatches(img1, kp1, img2, kp2, matches[:10], None, flags=2)
    #matplot_img(img3)
    disp_save_img(img3)


def main():
    
    # text menu
    def print_menu():  # Your menu design here
        print 30 * "-" , "MENU" , 30 * "-"
        print "1. Affine Transformation + matplotlib show + opencv display"
        print "2. Affine Transformation"
        print "3. Perspective Transformation"
        print "4. Fast Corner Detection"
        print "5. Track Good Features"
        print "6. Feature Matching with ORB"
        print "0. Exit"
        print 67 * "-"
      
    loop = True      
      
    while loop:  # While loop which will keep going until loop = False
        
        print_menu()  # Displays menu
        choice = input("Enter your choice: ")
         
        if choice == 1:     
            print "Menu 1 has been selected"
            fname = '/Users/ken/Pictures/5bucks.jpg'
            demo_5bucks(fname)
            #print 'bye from choice number 1'
        
        elif choice == 2:
            print "Menu 2 has been selected"
            fname = '/Users/ken/Pictures/perspective.png'
            img = load_img_gray(fname)
            affine_transformation(img)
        
        elif choice == 3:
            print "Menu 3 has been selected"
            fname = '/Users/ken/Pictures/garbage_affine.jpg'
            perspective_transformation(fname)
        
        elif choice == 4:
            print "Menu 4 has been selected"
            fname = '/Users/ken/Pictures/opencv-corner-detection-sample.jpg'
            fast_corner_detection(fname)
        
        elif choice == 5:
            print "Menu 5 has been selected"
            fname = '/Users/ken/Pictures/opencv-corner-detection-sample.jpg'
            track_good_features(fname)
            
        elif choice == 6:
            print "Menu 6 has been selected"
            orb_feature_matching()
            
        elif choice == 0:
            print "Menu 0 has been selected"
            ## You can add your code or functions here
            loop = False # This will make the while loop to end as not value of loop is set to False
        
        else:
            # Any integer inputs other than values 1-5 we print an error message
            raw_input("Wrong option selection. Enter any key to try again..")


if __name__ == '__main__':
    main()

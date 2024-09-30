#! python3

import cv2 as cv
import numpy as np
import itertools as it
import hashlib
import sys


# imgL = cv.imread('Photos-001/IMG_1005.jpeg', cv.IMREAD_GRAYSCALE);
# imgR = cv.imread('Photos-001/IMG_1006.jpeg', cv.IMREAD_GRAYSCALE);
# imgL = cv.imread('../Photos-001/IMG_1007.jpg', cv.IMREAD_GRAYSCALE)
# imgR = cv.imread('../Photos-001/IMG_1008.jpg', cv.IMREAD_GRAYSCALE)
imgL = cv.imread('../Photos-001/IMG_1007.jpg')
imgR = cv.imread('../Photos-001/IMG_1008.jpg')


# stereo = cv.StereoBM.create(numDisparities=0, blockSize=9)
stereo = cv.StereoSGBM_create(
    minDisparity=0,
    numDisparities=8,  # Adjust as needed
    blockSize=8,
    P1=8 * 3 * 5 * 5,
    P2=32 * 3 * 5 * 5,
    disp12MaxDiff=1,
    uniquenessRatio=10,
    speckleWindowSize=10,
    speckleRange=32,
    preFilterCap=63,
)


imgD = stereo.compute(imgL, imgR)
imgD = cv.normalize(imgD, None, 0, 255, cv.NORM_MINMAX, dtype=cv.CV_8UC1)
cv.imshow("imgD", imgD)

cv.waitKey(4000)

#! python3

import cv2 as cv
from time import sleep

capture_l = cv.VideoCapture(0)
capture_r = cv.VideoCapture(1)
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


while True:
  ret, frame_l = capture_l.read()
  ret, frame_r = capture_r.read()

  frame_d = stereo.compute(frame_l, frame_r)
  frame_d = cv.normalize(frame_d, None, 0, 255, cv.NORM_MINMAX, dtype=cv.CV_8UC1)

  cv.imshow("frame_l", frame_l)
  cv.imshow("frame_r", frame_r)
  cv.imshow("frame_d", frame_d)


  key = cv.waitKey(1000)
  if key == ord("1"):
    capture_l = cv.VideoCapture(0)
    print("reset left")
  elif key == ord("2"):
    capture_r = cv.VideoCapture(1)
    print("reset right")
  if key == ord('q'):
    break

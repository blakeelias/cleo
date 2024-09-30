#! python3

import cv2 as cv
from time import sleep

capture_l = cv.VideoCapture(0)
capture_r = cv.VideoCapture(1)
while True:
  ret, frame_l = capture_l.read()
  cv.imshow("frame_l", frame_l)
  ret, frame_r = capture_r.read()
  cv.imshow("frame_r", frame_r)
  key = cv.waitKey(1)
  if key == ord("1"):
    capture_l = cv.VideoCapture(0)
    print("reset left")
  elif key == ord("2"):
    capture_r = cv.VideoCapture(1)
    print("reset right")
  if key == ord('q'):
    break


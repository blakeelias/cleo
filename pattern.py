#! python3

import cv2 as cv
import numpy as np
import itertools as it
import hashlib
import sys


# width, height = 1920, 1080
width, height = 256, 144
color_depth = 6


i = 0
while True:
    i += 1
    temporal_nonce = "test value" + str(i)

    img_src = hashlib.shake_256(temporal_nonce.encode()).digest(height * width)

    pattern = np.zeros((height, width, 3), np.uint8)

    # for y in range(height):
    #   for x in range(width):
    #     pix_src = int(img_src[y//8 * width//8 + x//8])
    #     r = int(63 * (pix_src % 5))
    #     pix_src = int(pix_src // 5)
    #     g = int(63 * (pix_src % 5))
    #     pix_src = int(pix_src // 5)
    #     b = int(63 * (pix_src % 5))
    #     pattern[y][x] = (r,g,b)

    for y in range(height):
        for x in range(width):
            r_src = img_src[y//2 * width//2 + x//2]
            g_src = img_src[y//1 * width//1 + x//1]
            b_src = img_src[y//4 * width//4 + x//4]
            r = 254//(color_depth-1) * ((r_src//color_depth**0) % color_depth)
            g = 254//(color_depth-1) * ((g_src//color_depth**1) % color_depth)
            b = 254//(color_depth-1) * ((b_src//color_depth**2) % color_depth)
            pattern[y][x] = (r, g, b)

    # pattern[:,0:width//2] = (255,0,0)
    # pattern[:,width//2:width] = (0,255,0)

    pattern = cv.resize(pattern, (0, 0), fx=8, fy=8,
                        interpolation=cv.INTER_NEAREST)
    pattern = cv.cvtColor(pattern, cv.COLOR_RGB2BGR)
    cv.imshow("pattern", pattern)
    cv.waitKey(10)

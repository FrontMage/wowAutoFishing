import time
import cv2
import mss
import numpy as np
from pynput.keyboard import Key, Controller
from pynput.mouse import Button, Controller as MouseController

keyboard = Controller()
mouse = MouseController()
while True:
    # start fishing wiht hotkey "z"
    keyboard.press("z")
    keyboard.release("z")
    time.sleep(1)
    # capture the positon of the float
    sct = mss.mss()
    monitor = sct.monitors[0]
    time.sleep(1)
    img_rgb = np.array(sct.grab(monitor))

    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread('float.png',0)
    w, h = template.shape[::-1]

    res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)

    click_point = (bottom_right + top_left)/2
    # cv2.rectangle(img_rgb, top_left, bottom_right, (0,0,255), 2)

    # Display the picture
    # cv2.imshow("Screenshot", img_rgb)

    # Press "q" to quit
    # if cv2.waitKey(25) & 0xFF == ord("q"):
    #     cv2.destroyAllWindows()
    #     break


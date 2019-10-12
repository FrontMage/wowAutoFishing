import threading
from array import array
from queue import Queue, Full

import pyaudio
import time
import cv2
import mss
import numpy as np
from pynput.keyboard import Key, Controller
from pynput.mouse import Button, Controller as MouseController

keyboard = Controller()
mouse = MouseController()

CHUNK_SIZE = 1024
MIN_VOLUME = 1500
# if the recording thread can't consume fast enough, the listener will start discarding
BUF_MAX_SIZE = CHUNK_SIZE * 10


def main():
    stopped = threading.Event()
    q = Queue(maxsize=int(round(BUF_MAX_SIZE / CHUNK_SIZE)))

    listen_t = threading.Thread(target=listen, args=(stopped, q))
    listen_t.start()
    record_t = threading.Thread(target=record, args=(stopped, q))
    record_t.start()

    try:
        while True:
            listen_t.join(0.1)
            record_t.join(0.1)
    except KeyboardInterrupt:
        stopped.set()

    listen_t.join()
    record_t.join()

def get_click_point():
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

    click_point = ((bottom_right[0] + top_left[0])/2, (bottom_right[1]+top_left[1])/2)
    return click_point

def start_fishing():
    # start fishing wiht hotkey "z"
    keyboard.press("z")
    keyboard.release("z")

def click_the_bait(click_point):
    mouse.move(click_point)
    mouse.click(Button.right)

def record(stopped, q):
    is_fishing = False
    thresh_reach_count = 0
    start_fishing_time = time.time()
    while True:
        if stopped.wait(timeout=0):
            break
        # timeout after 30s, restart everything
        if time.time() - start_fishing_time > 30:
            is_fishing = 0
            thresh_reach_count = 0
            start_fishing_time = time.time()
        if not is_fishing:
            start_fishing()
            time.sleep(1)
            click_point = get_click_point()
            is_fishing = True
        chunk = q.get()
        vol = max(chunk)
        if vol >= MIN_VOLUME:
            thresh_reach_count = thresh_reach_count+1
            print("O"),
        else:
            thresh_reach_count = 0
        if thresh_reach_count>3:
            click_the_bait(click_point)
            time.sleep(5)
            is_fishing = False


def listen(stopped, q):
    stream = pyaudio.PyAudio().open(
        format=pyaudio.paInt16,
        channels=2,
        rate=44100,
        input=True,
        frames_per_buffer=1024,
    )

    while True:
        if stopped.wait(timeout=0):
            break
        try:
            q.put(array('h', stream.read(CHUNK_SIZE)))
        except Full:
            pass  # discard


if __name__ == '__main__':
    main()

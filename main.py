import threading
from array import array
from queue import Queue, Full
import pyaudio
import time
import cv2
import mss
import numpy as np
import pyautogui

CHUNK_SIZE = 1024
MIN_VOLUME = 1000
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
            # listen_t.join(0.1)
            record_t.join(0.1)
    except KeyboardInterrupt:
        stopped.set()

    listen_t.join()
    record_t.join()

def get_click_point(target):
    # capture the positon of the float
    points = []
    for _ in range(9):
        with  mss.mss() as sct:
            monitor = sct.monitors[0]
            time.sleep(0.1)
            img_rgb = np.array(sct.grab(monitor))

            img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
            template = cv2.imread(target,0)
            w, h = template.shape[::-1]

            res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)

            click_point = ((bottom_right[0] + top_left[0])/2, (bottom_right[1]+top_left[1])/2)
            points.append(click_point)
            # debug_img(img_rgb, top_left, bottom_right)
    points.sort(key=lambda tup:tup[0])
    return points[5]

def debug_img(img_rgb, top_left, bottom_right):
    cv2.rectangle(img_rgb, top_left, bottom_right, (0,0,255), 2)
    cv2.imwrite("debug.png", img_rgb)

def start_fishing():
    click_point = get_click_point('fishing_skill.png')
    click_the_bait(click_point)

def click_the_bait(click_point):
    print(click_point)
    pyautogui.moveTo(click_point[0], click_point[1], 1, pyautogui.easeInOutQuad)
    time.sleep(300/1000)
    pyautogui.click(button="right")

def record(stopped, q):
    is_fishing = False
    thresh_reach_count = 0
    start_fishing_time = time.time()
    max_inactive_sound_gap = 0
    start_time = time.time()
    # give some time to switch window focus
    time.sleep(5)
    while True:
        if stopped.wait(timeout=0):
            break
        # auto get bait buff
        # if time.time()-start_time>60*10:
        #     click_point = get_click_point('bait.png')
        #     click_the_bait(click_point)
        #     time.sleep(6)
        #     start_time = time.time()
        # timeout after 30s, restart everything
        if time.time() - start_fishing_time > 30:
            is_fishing = False
            thresh_reach_count = 0
            start_fishing_time = time.time()
        if not is_fishing:
            print("Start fishing")
            start_fishing()
            time.sleep(1)
            click_point = get_click_point('float3.png')
            is_fishing = True
        chunk = q.get()
        vol = max(chunk)
        if vol >= MIN_VOLUME:
            # ignore the first fishing sound
            if time.time() - start_fishing_time > 10:
                thresh_reach_count = thresh_reach_count+1
                max_inactive_sound_gap = 0
                print("O"),
        else:
            # only clears thresh after more than 15 no sound frame
            if max_inactive_sound_gap > 2048:
                thresh_reach_count = 0
            # print("-")
            max_inactive_sound_gap = max_inactive_sound_gap + 1
        if thresh_reach_count>1:
            print("Clicking bait")
            click_the_bait(click_point)
            time.sleep(5)
            is_fishing = False
            thresh_reach_count = 0
            start_fishing_time = time.time()


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

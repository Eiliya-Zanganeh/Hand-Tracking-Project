from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import math
import numpy as np
import cv2
import time

from Modules.HandTracking import handTrackingModule as mp
w = 640
h = 480

video = cv2.VideoCapture(1)
video.set(3, w)
video.set(4, h)
ptime = 0

detetor = mp.handDetector()

device = AudioUtilities.GetSpeakers()
interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()

minVol = volRange[0]
maxVol = volRange[1]
while True:
    success, img = video.read()
    img = detetor.findHands(img)
    hands = detetor.findPosition(img, draw=False)
    # print(hands)
    if len(hands) != 0:
        x1, y1 = hands[0][1][4][1], hands[0][1][4][2]
        x2, y2 = hands[0][1][8][1], hands[0][1][8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(img, (x1, y1), 10, (0, 255, 0), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (0, 255, 0), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)
        cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)
        # print(length)

        vol = np.interp(length, [50, 300], [minVol, maxVol])
        volume.SetMasterVolumeLevel(vol, None)

        if length < 50:
            cv2.circle(img, (cx, cy), 10, (0, 0, 255), cv2.FILLED)

    ctime = time.time()
    fps = 1 / (ctime - ptime)
    ptime = ctime

    cv2.putText(img, f'FPS {int(fps)}', (20, 700), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)

    cv2.imshow('img', img)
    cv2.waitKey(1)

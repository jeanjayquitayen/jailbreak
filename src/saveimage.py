import _thread as thread
import queue as Queue
import cv2
import datetime
import time


def savephoto(imgs):
         time = datetime.datetime.now().strftime("%m-%d-%Y-%I-%M-%S")
         cv2.imwrite('../captures/' + time + '.jpg', imgs)



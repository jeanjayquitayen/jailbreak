import datetime
import cv2
import os

SRC_PATH = os.getcwd()

BASE_PATH = os.path.split(SRC_PATH)[0]
CAPTURE_PATH = os.path.join(BASE_PATH, "captures")

def savephoto(imgs):
    cap_time = datetime.datetime.now().strftime("%m-%d-%Y-%I-%M-%S")
    cv2.imwrite(os.path.join(CAPTURE_PATH, cap_time) + '.jpg', imgs)

if __name__ == "__main__":
    pass

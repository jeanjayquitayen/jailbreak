#!/usr/bin/python3

# import the necessary packages
import datetime
import os
import signal
import sys
import time
import configparser
import threading
from contextlib import contextmanager

import imutils
from cv2 import cvtColor, THRESH_BINARY, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE, destroyAllWindows
from cv2 import GaussianBlur, absdiff, threshold, dilate, findContours, FONT_HERSHEY_SIMPLEX, waitKey
from cv2 import contourArea, imwrite, COLOR_BGR2GRAY, imshow, putText, rectangle, boundingRect
from cv2 import error as cv2_error
import sms
from contacts_writer import readCSV
from picamera.array import PiRGBArray
from picamera import PiCamera

try:
    contacts = list(readCSV().values())

except FileNotFoundError as err:
    sys.exit(err)


def multicast_message(contact_arr):
    for i in contact_arr:
        gsm.sendMessage(JAILBREAK_INI['Message'], i)

def save_photo(imgs):
    cap_time = datetime.datetime.now().strftime("%m-%d-%Y-%I-%M-%S")
    imwrite(os.path.join(CAPTURE_PATH, cap_time) + '.jpg', imgs)

def sig_handler(sig, signal_frame):
    camera.release()
    destroyAllWindows()
    sys.exit(0)

def show_feed(frame):
    # compute the bounding box for the contour, draw it on the frame,
    # and update the text
    putText(frame, "Room Status: {}".format(text), (10, 20),
        FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
        (10, frame.shape[0] - 10), FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

    #show the frame and record if the user presses a key
    imshow("Security Feed", frame)
    # imshow("Thresh", thresh)
    # imshow("Frame Delta", frameDelta)

def put_rect_frame(frame,c):
    """Encluse Object with rectangle"""
    (x, y, w, h) = boundingRect(c)
    rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

@contextmanager
def capture_frame():
    # grab the current frame
    raw_image = camera.capture_continuous(rawCapture, format="bgr", use_video_port=True)
    yield raw_image
    rawCapture.truncate(0)


def prepare_image(frame):
    """resize the frame, convert it to grayscale, and blur it"""
    # frame = imutils.resize(frame, width=500)
    gray = cvtColor(frame, COLOR_BGR2GRAY)
    gray = GaussianBlur(gray, (21, 21), 0) #noise filtering
    return gray

def background_subtraction(gray):
    """Perfroms background subrtraction, thresholding and finding contours"""
    # compute the absolute difference between the current frame and first frame
    frame_delta = absdiff(firstFrame, gray) #get the difference between the two frames
    thresh = threshold(frame_delta, 150, 255, THRESH_BINARY)[1]

    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    thresh = dilate(thresh, None, iterations=2)
    (cnts, _) = findContours(thresh.copy(), RETR_EXTERNAL, CHAIN_APPROX_SIMPLE)
    return cnts


if __name__ == "__main__":
    CONF = configparser.ConfigParser()
    assert CONF.read('config.ini'), "No config.ini file found. \
        Please create config.ini using create_config.py"       
    SERIAL_INI = CONF['pyserial']
    JAILBREAK_INI = CONF['jailbreak']
    NODENAME = os.uname()[1]
    # if NODENAME == "raspberrypi":
    #     IS_PI = True
    # else:
    #     IS_PI = False
    # initialize the first frame in the video stream
    firstFrame = None
    counter = 0
    # loop over the frames of the video
    SRC_PATH = os.getcwd()
    BASE_PATH = os.path.split(SRC_PATH)[0]
    CAPTURE_PATH = os.path.join(os.path.realpath(BASE_PATH), "captures")

    signal.signal(signal.SIGINT, sig_handler)
    try:
        camera = PiCamera()
        camera.resolution = (640, 480)
        camera.framerate = 32
        rawCapture = PiRGBArray(camera, size=(640, 480))
        time.sleep(0.1)
    finally:
        gsm = sms.SMS(SERIAL_INI['Port'], int(SERIAL_INI['Baudrate']), int(SERIAL_INI['Timeout']))
        


    print(JAILBREAK_INI['Console_txt'])
    print("#" * 100)
    print("Minimum area: {}".format(int(CONF['cv']['Min-area'])))
    text = JAILBREAK_INI['Unoccupied']
    for raw_image in  camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        frame = raw_image.array
        orig_frame = frame
        gray = prepare_image(frame)
        # if the first frame is None, initialize it
        rawCapture.truncate(0)
        if firstFrame is None:
            firstFrame = gray #this is the reference frame , edit ang flowchart mali pala yon
            continue
        for c in background_subtraction(gray):
            # if the contour is too small, ignore it
            if contourArea(c) < int(CONF['cv']['Min-area']):
                continue #go back to capturing frame if the threshold was not met
            put_rect_frame(frame, c)

            text = JAILBREAK_INI['Occupied']
            show_feed(frame)

                # draw the text and timestamp on the frame
        print("Room Status: {}".format(text), end="\r")
        if "Motion" in text:
            counter += 1
            if counter > 40:
                counter = 0
                print("Saving Photo")
                t = threading.Thread(group=None, target=multicast_message, args=(contacts,))
                t.start()
                save_photo(orig_frame)
        key = waitKey(1) & 0xFF
        #if the `q` key is pressed, break from the loop
        if key == ord("q"):
            break
        
    # cleanup the camera and close any open windows
    # try:
    #     camera.release()
    #     destroyAllWindows()

#!/usr/bin/python3

# import the necessary packages
import argparse
import datetime
import os
import signal
import sys
import time
import imutils
from cv2 import cvtColor, VideoCapture, THRESH_BINARY, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE
from cv2 import GaussianBlur, absdiff, threshold, dilate, findContours
from cv2 import contourArea, imwrite, COLOR_BGR2GRAY
import sms
from contacts_writer import readCSV
import _thread as thread

contacts = list(readCSV().values())
uname = os.uname()
nodename = uname[1]



# gsm = sms.SMS("/dev/ttyUSB0",9600,None)

#construct the argument parser and parse the arguments

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=50, help="minimum area size")
args = vars(ap.parse_args())

# if the video argument is None, then we are reading from webcam
if args.get("video", None) is None:
    if nodename == "raspberrypi":
        from picamera.array import PiRGBArray
        from picamera import PiCamera
        gsm = sms.SMS("/dev/ttyUSB0",115200,1)
        camera = PiCamera()
        camera.resolution = (640, 480)
        camera.framerate = 32
        rawCapture = PiRGBArray(camera, size=(640, 480))
        pi_camera_gen = None
        time.sleep(0.1)
    else:
        gsm = sms.SMS("/dev/ttyUSB0",115200,1)
        camera = VideoCapture(0)
        time.sleep(0.25)

# otherwise, we are reading from a video file
else:
    camera = VideoCapture(args["video"])

# initialize the first frame in the video stream
firstFrame = None
counter = 0
# loop over the frames of the video
SRC_PATH = os.getcwd()
BASE_PATH = os.path.split(SRC_PATH)[0]
CAPTURE_PATH = os.path.join(os.path.realpath(BASE_PATH), "captures")

def multicastMessage(contact_arr):
    for i in contact_arr:
        gsm.sendMessage("PRISON BREAK ALERT! CONDUCT IMMEDIATE RESPONSE!",i)

def savephoto(imgs):
    cap_time = datetime.datetime.now().strftime("%m-%d-%Y-%I-%M-%S")
    imwrite(os.path.join(CAPTURE_PATH, cap_time) + '.jpg', imgs)

def sigHandler(sig, signal_frame):
    if "raspberrypi" not in nodename:
        camera.release()
    # cv2.destroyAllWindows()
    sys.exit(0)
signal.signal(signal.SIGINT, sigHandler)
print("JailBreak Prototype Version\nFor education use only\nThe creators held no liabilities \
    for any damages and problem due to miss use of these app.\nDevelopers: \ns")
print("#" * 100)
print("Minimum area: {}".format(args["min_area"]))

while True:
    # grab the current frame and initialize the occupied/unoccupied
    # text
    if nodename == "raspberrypi" and not pi_camera_gen == "end":
        raw_image = camera.capture_continuous(rawCapture, format="bgr", use_video_port=True)
        rawCapture.truncate(0)
        pi_camera_gen = next(raw_image, "end")
        if pi_camera_gen == "end":
            pi_camera_gen = None
            continue
        frame = pi_camera_gen.array
    else:
        (grabbed, frame) = camera.read()
        if not grabbed:
            break
    text = "Unoccupied      "
    orig_frame = frame
    # resize the frame, convert it to grayscale, and blur it
    # frame = imutils.resize(frame, width=500)
    gray = cvtColor(frame, COLOR_BGR2GRAY)
    gray = GaussianBlur(gray, (21, 21), 0) #noise filtering

    # if the first frame is None, initialize it
    if firstFrame is None:
        firstFrame = gray #this is the reference frame , edit ang flowchart mali pala yon
        continue
    # compute the absolute difference between the current frame and
    # first frame
    frameDelta = absdiff(firstFrame, gray) #get the difference between the two frames
    thresh = threshold(frameDelta, 150, 255, THRESH_BINARY)[1]

    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    thresh = dilate(thresh, None, iterations=2)
    (cnts,_) = findContours(thresh.copy(), RETR_EXTERNAL, CHAIN_APPROX_SIMPLE)

    for c in cnts:
        # if the contour is too small, ignore it
        if contourArea(c) < args["min_area"]:
            continue #go back to capturing frame if the threshold was not met

        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        # uncomment to show rectangle
        # (x, y, w, h) = cv2.boundingRect(c)
        # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        text = "Motion Detected!"

            # draw the text and timestamp on the frame
    print("Room Status: {}".format(text), end="\r")
    if "Motion" in text:
        counter += 1
        if counter > 40:
            counter = 0
            print("Saving Photo")
            thread.start_new_thread(multicastMessage, (contacts,))
            savephoto(orig_frame)


    #uncomment to show feed
    # cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
    #     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    # cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
    #     (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

    # show the frame and record if the user presses a key
    # cv2.imshow("Security Feed", frame)
    # cv2.imshow("Thresh", thresh)
    # cv2.imshow("Frame Delta", frameDelta)
    # key = cv2.waitKey(1) & 0xFF

    # if the `q` key is pressed, break from the loop
    # if key == ord("q"):
    #     break

# cleanup the camera and close any open windows
if "raspberrypi" not in nodename:
    camera.release()
# cv2.destroyAllWindows()

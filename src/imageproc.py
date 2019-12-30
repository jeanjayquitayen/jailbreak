#!/usr/bin/python3

# import the necessary packages
import argparse
import datetime
import os
import signal
import sys
import time
import imutils
import cv2
import sms
# import _thread as thread




# gsm = sms.SMS("/dev/ttyUSB0",9600,None)

#construct the argument parser and parse the arguments

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=50, help="minimum area size")
args = vars(ap.parse_args())

# if the video argument is None, then we are reading from webcam
if args.get("video", None) is None:
    camera = cv2.VideoCapture(0)
    time.sleep(0.25)

# otherwise, we are reading from a video file
else:
    camera = cv2.VideoCapture(args["video"])

# initialize the first frame in the video stream
firstFrame = None
counter = 0
# loop over the frames of the video
SRC_PATH = os.getcwd()
BASE_PATH = os.path.split(SRC_PATH)[0]
CAPTURE_PATH = os.path.join(os.path.realpath(BASE_PATH), "captures")

def savephoto(imgs):
    cap_time = datetime.datetime.now().strftime("%m-%d-%Y-%I-%M-%S")
    cv2.imwrite(os.path.join(CAPTURE_PATH, cap_time) + '.jpg', imgs)

def sigHandler(sig, signal_frame):
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
    (grabbed, frame) = camera.read()
    text = "Unoccupied"

    # if the frame could not be grabbed, then we have reached the end
    # of the video
    if not grabbed:
        break
    orig_frame = frame
    # resize the frame, convert it to grayscale, and blur it
    frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0) #noise filtering

    # if the first frame is None, initialize it
    if firstFrame is None:
        firstFrame = gray #this is the reference frame , edit ang flowchart mali pala yon
        continue# compute the absolute difference between the current frame and
    # first frame
    frameDelta = cv2.absdiff(firstFrame, gray) #get the difference between the two frames
    thresh = cv2.threshold(frameDelta, 150, 255, cv2.THRESH_BINARY)[1]

    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    (cnts,_) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # loop over the contours
    
    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < args["min_area"]:
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
            # thread.start_new_thread(savephoto, (frame,))
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
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key is pressed, break from the loop
    if key == ord("q"):
        break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()

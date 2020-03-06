#!/usr/bin/python3

# import the necessary packages
import datetime
import os
import signal
import sys
import time
import configparser
import threading
import queue
from contextlib import contextmanager
import logging
from cv2 import cvtColor, THRESH_BINARY, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE, destroyAllWindows
from cv2 import GaussianBlur, absdiff, threshold, dilate, findContours, FONT_HERSHEY_SIMPLEX, waitKey
from cv2 import contourArea, imwrite, COLOR_BGR2GRAY, imshow, putText, rectangle, boundingRect
from cv2 import error as cv2_error
import sms
from contacts_writer import readCSV
from picamera.array import PiRGBArray
from picamera import PiCamera
from dropboxx import main
from gpiozero import LED

q = queue.Queue()
qsms = queue.Queue()
led = LED(17) # Choose the correct pin number
led.off()
alarm = False
def multicast_message(contact_arr):
    #gsm.sendMessageAndSave(JAILBREAK_INI['Message'],contact_arr.pop())
    for i in contact_arr:
        try:
            gsm.sendMessage(JAILBREAK_INI['Message'], i)
            time.sleep(3)
            logger.info("SMS SENT")
        except:
            logger.warning("SMS FAILED")
    gsm.setToGsm()

def save_photo(imgs):
    cap_time = datetime.datetime.now().strftime("%m-%d-%Y-%I-%M-%S")
    imwrite(os.path.join(CAPTURE_PATH, cap_time) + '.jpg', imgs)

def sig_handler(sig, signal_frame):
    # destroyAllWindows()
    q.put(40)
    logger.info("APP EXIT")
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

def prepare_image(frame):
    """resize the frame, convert it to grayscale, and blur it"""
    # frame = imutils.resize(frame, width=500)
    gray_img = cvtColor(frame, COLOR_BGR2GRAY)
    gray_img = GaussianBlur(gray_img, (21, 21), 0) #noise filtering
    return gray_img

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
def queue_save_photos():
    while True:
        if not q.empty():
            data = q.get()
            try:
                if data == 40:
                    break
            except ValueError as err:
                # app_logger.warning(err)
                pass    
            finally:
                save_photo(q.get())

def queue_sms(contacts):
    while True:
        if not qsms.empty():
            if qsms.get():
                multicast_message(contacts)
                time.sleep(5)

def uploadImages():
    while True:
        try:
            main()
        except:
            print("Can't Upload")
            print("Can't Upload")

if __name__ == "__main__":

    try:
        CONTACTS = list(readCSV().values())
        print(CONTACTS)
    except FileNotFoundError as err:
        logger.error(err)
        sys.exit(err)

        # create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # create file handler and set level to debug
    ch = logging.FileHandler("../captures/" + datetime.datetime.now().strftime("%m-%d-%Y-%I-%M-%S") + ".log")
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to loggerDEBUG
    logger.addHandler(ch)
    CONF = configparser.ConfigParser()
    try:
        assert CONF.read('config.ini'), "No config.ini file found. \
            Please create config.ini using create_config.py"
    except AssertionError as err:
        logger.error(err)       
    SERIAL_INI = CONF['pyserial']
    JAILBREAK_INI = CONF['jailbreak']

    # NODENAME = os.uname()[1]
    # if NODENAME == "raspberrypi":
    #     IS_PI = True
    # else:
    #     IS_PI = False
    # initialize the first frame in the video stream
    firstFrame = None
    
    # loop over the frames of the video
    SRC_PATH = os.getcwd()
    BASE_PATH = os.path.split(SRC_PATH)[0]
    CAPTURE_PATH = os.path.join(os.path.realpath(BASE_PATH), "captures")

    signal.signal(signal.SIGINT, sig_handler)
    try:
        camera = PiCamera()
        camera.resolution = (640, 480)
        camera.framerate = 16
        RAW_CAPTURE = PiRGBArray(camera, size=(640, 480))
        time.sleep(10) # Delay on start
    except:
        sys.exit(0)
        logger.error("Picamera Init Error")
    try:
        gsm = sms.SMS(SERIAL_INI['Port'], int(SERIAL_INI['Baudrate']), int(SERIAL_INI['Timeout']))
    except:
        logger.error("GSMS Serial Init Error")
        
    gsm.setToGsm()

    print(JAILBREAK_INI['Console_txt'])
    print("#" * 100)
    print("Minimum area: {}".format(int(CONF['cv']['Min-area'])))
    DROPBOX_THREAD = threading.Thread(group=None, target=uploadImages)
    DROPBOX_THREAD.daemon = True
    DROPBOX_THREAD.start()
    SEND_THREAD = threading.Thread(group=None, target=queue_sms, args=(CONTACTS,))
    SAVE_THREAD = threading.Thread(group=None, target=queue_save_photos)
    SAVE_THREAD.daemon = True
    SAVE_THREAD.start()
    #SEND_THREAD.daemon = True
    SEND_THREAD.start()
    time_last_sent = 0
    time_now = 0
    send_SMS = False
    for raw_image in  camera.capture_continuous(RAW_CAPTURE, format="bgr", use_video_port=True):
        frame = raw_image.array
        orig_frame = frame
        gray = prepare_image(frame)
        text = JAILBREAK_INI['Unoccupied'] + "      " #6 spaces
        Area_contour = 0
        # if the first frame is None, initialize it
        RAW_CAPTURE.truncate(0)
        if firstFrame is None:
            firstFrame = gray #this is the reference frame , edit ang flowchart mali pala yon
            continue
        for c in background_subtraction(gray):
            # if the contour is too small, ignore it
            Area_contour = contourArea(c)
            if Area_contour < int(CONF['cv']['Min-area']):
                continue #go back to capturing frame if the threshold was not met
            #put_rect_frame(frame, c)
            text = JAILBREAK_INI['Occupied']
            
        #show_feed(frame)
        print("Room Status: {}".format(text))
        print("Threshold: {}\tContourArea: {}".format(CONF['cv']['Min-area'], Area_contour))
        if "Motion" in text:
            q.put(orig_frame)
            time_now = time.time()
            if (time_now - time_last_sent) >= int(CONF['sendSMS']['delay']):
                if time_last_sent == 0:
                    time_last_sent = time_now
                    continue
                send_SMS = True
                print("SENDING SMS")
                if send_SMS:
                    print("SENDING SMS NOW")
                    logger.info("SENDING SMS")
                    if(not alarm):
                        alarm = True
                        led.on()
                    qsms.put(True)
                    time_last_sent = time.time()
                    send_SMS = False

        #key = waitKey(1) & 0xFF
        #if the `q` key is pressed, break from the loop
        #if key == ord("q"):
           # break
        


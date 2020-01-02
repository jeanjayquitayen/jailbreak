import serial
import re
import _thread as thread
import queue as Queue
import time
import csv
import os
from datetime import datetime

import sim800USB



class SMS(sim800USB.sim800USB):
    def __init__(self,port,baud,timeout):
        super().__init__(port,baud,timeout)
        #SMS Commands/functions/methods
    def sendMessage(self,message,phonenumber):
        ret = self.sendAtCommand("AT+CMGF=1") #SMS system to textmode
        time.sleep(0.05)
        ret = self.sendAtCommand("AT+CSCS=\"GSM\"")
        time.sleep(0.05)
        ret = self.sendAtCommand("AT+CMGS=\"{}\"".format(phonenumber))
        # time.sleep(0.1)
        ret = self.sendAtCommand(message,endfeed="\u001A")
        if not ret:
            print("cant send")
        print(ret)
        

if __name__ == "__main__":
    sms = SMS(port = "/dev/ttyUSB0",baud=115200,timeout=1)
    sms.sendMessage("Kigul ni Reina","09203143780")

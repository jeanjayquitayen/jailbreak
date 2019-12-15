
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
        

 

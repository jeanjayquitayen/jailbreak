import serial


class sim800USB(serial.Serial):
    def __init__(self,port,baud,timeout):
        super().__init__(port="/dev/ttyUSB0",baud=115200,timeout=None)

    def sendAtCommand(self,at_command):
        self.write((at_command + "\r").encode())
        self.flush()
        ret = self.process()
        return ret

    def handleResponse(self):
        if self.in_waiting:
            self.readline() #consume first line
            yield  (self.read(self.in_waiting)).decode()

    def process(self):
        data = self.handleResponse()
        d = [i for i in data]
        if len(d) != 0:
            return d

    def unpackData(self, generator):
        resp_list = list()
        for i in generator:
            resp_list.append(i.strip('\r\n'))
        del generator
        return resp_list

    #SMS Commands/functions/methods
    def sendMessage(self,message,phonenumber):
        self.sendAtCommand("AT+CMGF=1") #SMS system to textmode
        self.sendAtCommand("AT+CSCS=GSM")
        self.sendAtCommand("AT+CMGS={}".format(phonenumber))
        ret = self.sendAtCommand("{}".format(message))
        if not ret:
            raise "Can't send SMS."
    
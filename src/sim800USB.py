import serial
import time

class sim800USB(serial.Serial):
    def __init__(self,port="/dev/ttyS0",baudrate=9600,tout=1):
        super().__init__(port,baudrate,timeout=tout)

    def sendAtCommand(self,at_command,endfeed="\r"):
        self.write((at_command + endfeed).encode())
        self.flush()
        ret = self.process()
        return ret

    def handleResponse(self):
        # print(self.read(self.in_waiting).decode())
        _ = self.readline()
        x = self.read(self.in_waiting) #consume first line
        return x.decode()
        

    def process(self):
        data = self.handleResponse()
        return data
        # d = [i for i in data]
        # if len(d) != 0:
        #     return d

    def unpackData(self, generator):
        resp_list = list()
        for i in generator:
            resp_list.append(i.strip('\r\n'))
        del generator
        return resp_list




if __name__ == "__main__":
    sms = sim800USB()
    sms.sendMessage("testing","+639176356924")
    # ret = sms.sendAtCommand("AT+CMGS=\"+639176356924\"")
    print(sms.isOpen())
    sms.close()
    print(sms.isOpen())


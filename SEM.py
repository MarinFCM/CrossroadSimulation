import socket
import threading
import time

SEMstate = None


class RecieveState(threading.Thread):
    def __init__(self, TSlock, UPRpipe):
        threading.Thread.__init__(self)
        self.TSlock = TSlock
        self.UPRpipe = UPRpipe

    def run(self):
        global SEMstate

        while True:
            if self.UPRpipe.poll():
                self.TSlock.acquire()
                SEMstate = self.UPRpipe.recv()[0]
                self.print('[SEM-STATE]: ' + SEMstate + " is the new SEM state!")
                self.TSlock.release()
            else:
                time.sleep(0.2)

    def print(self, toPrint):
        with open("SEM_STATE.log", 'a') as f:
            f.write(toPrint + '\n')


class ServerPC(threading.Thread):
    def __init__(self, TSlock, Connection):
        threading.Thread.__init__(self)
        self.TSlock = TSlock
        self.host = Connection[0]
        self.port = Connection[1]
        self.sock = None

    def run(self):
        global SEMstate

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))

        while True:
            data, clientAddr = self.sock.recvfrom(20)
            data = data.decode()
            self.print('[SEM-UDP]: ' + data + " wants to know SEM state!")
            toReturn = self.checkLight(data)
            if toReturn:
                self.sock.sendto(b'1', clientAddr)
            else:
                self.sock.sendto(b'0', clientAddr)

    def checkLight(self, data):
        light = False
        if data[0] == 'C':
            if data[2] == 'N' or data[2] == 'S':
                self.TSlock.acquire()
                light = SEMstate[0:4] == 'GGRR'
                self.TSlock.release()
            elif data[2] == 'E' or data[2] == 'W':
                self.TSlock.acquire()
                light = SEMstate[0:4] == 'RRGG'
                self.TSlock.release()
            return light
        elif data[0] == 'P':
            if data[2:] == 'NW-SW' or data[2:] == 'SW-NW' or data[2:] == 'SE-NE' or data[2:] == 'NE-SE':
                self.TSlock.acquire()
                light = SEMstate[5:] == 'RRGG'
                self.TSlock.release()
            elif data[2:] == 'NW-NE' or data[2:] == 'NE-NW' or data[2:] == 'SE-SW' or data[2:] == 'SE-SW':
                self.TSlock.acquire()
                light = SEMstate[5:] == 'GGRR'
                self.TSlock.release()
            return light

    def print(self, toPrint):
        with open("SEM_UDP.log", 'a') as f:
            f.write(toPrint + '\n')


def init(UPRpipe, Connection):
    TrafficStateLock = threading.Lock()
    recieveThread = RecieveState(TrafficStateLock, UPRpipe)
    stateThread = ServerPC(TrafficStateLock, Connection)

    recieveThread.start()
    stateThread.start()

import socket
import threading
import time


class Car(threading.Thread):
    def __init__(self, direction, UPRqueue, SEMconnection, RASqueue):
        self.direction = direction
        self.UPRqueue = UPRqueue
        self.SEMconnection = SEMconnection
        self.SEMsock = None
        self.RASqueue = RASqueue
        threading.Thread.__init__(self)

    def run(self):
        CROSS_TIME = 5
        CHECK_LIGHT_DELAY = 1
        self.SEMsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.UPRqueue.put(['C-' + self.direction, ])
        self.RASqueue.put(['C-' + self.direction, ])
        canPass = False
        while not canPass:
            self.SEMsock.sendto(('C-' + self.direction).encode(), (self.SEMconnection[0], self.SEMconnection[1]))
            if self.SEMsock.recv(1) == b'1':
                print('Car from', self.direction, ' saw a green light!')
                canPass = True
            else:
                #print('Car from', self.direction, ' saw a red light!')
                time.sleep(CHECK_LIGHT_DELAY)

        self.RASqueue.put(['S-C-' + self.direction, ])
        print('Car from', self.direction, ' heading into intersection!')

        time.sleep(CROSS_TIME)

        self.RASqueue.put(['D-C-' + self.direction, ])
        print('Car from', self.direction, ' left intersection!')


class Pedestrian(threading.Thread):
    def __init__(self, direction, UPRqueue, SEMconnection, RASqueue):
        self.direction = direction
        self.UPRqueue = UPRqueue
        self.SEMconnection = SEMconnection
        self.SEMsock = None
        self.RASqueue = RASqueue
        threading.Thread.__init__(self)

    def run(self):
        CROSS_TIME = 10
        CHECK_LIGHT_DELAY = 1
        self.UPRqueue.put(['P-' + self.direction, ])
        self.RASqueue.put(['P-' + self.direction, ])
        self.SEMsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        canPass = False
        while not canPass:
            self.SEMsock.sendto(('P-' + self.direction).encode(), (self.SEMconnection[0], self.SEMconnection[1]))
            if self.SEMsock.recv(1) == b'1':
                print('Pederstrian going', self.direction, 'saw a green light!')
                canPass = True
            else:
                #print('Pederstrian going', self.direction, 'saw a red light!')
                time.sleep(CHECK_LIGHT_DELAY)

        self.RASqueue.put(['S-P-' + self.direction, ])
        print('Pedestrian going', self.direction, 'heading onto crosswalk!')

        time.sleep(CROSS_TIME)

        self.RASqueue.put(['D-P-' + self.direction, ])
        print('Pedestrian going', self.direction, 'left crosswalk!')

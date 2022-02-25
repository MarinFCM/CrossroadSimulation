import threading
import time


class TrafficState:
    def __init__(self):
        self.carWait = {'N': False, 'S': False, 'E': False, 'W': False}

        self.pedWait = {'SW-SE': False, 'SW-NW': False, 'SE-SW': False, 'SE-NE': False, 'NW-NE': False, 'NW-SW': False,
                        'NE-SE': False, 'NE-NW': False}

        self.SEMstate = None
        self.lastSEMstate = "RRGG-GGRR"

    def isPedWaiting(self, side):
        if side == 'N' or side == 'S':
            if self.pedWait['NE-SE'] or self.pedWait['SE-NE'] or self.pedWait['NW-SW'] or self.pedWait['SW-NW']:
                return True
            else:
                return False
        else:
            if self.pedWait['NE-NW'] or self.pedWait['NW-NE'] or self.pedWait['SE-SW'] or self.pedWait['SW-SE']:
                return True
            else:
                return False

    def isCarWaiting(self, side):
        if side == 'E' or side == 'W':
            if self.carWait['E'] or self.carWait['W']:
                return True
            else:
                return False
        else:
            if self.carWait['N'] or self.carWait['S']:
                return True
            else:
                return False


trafficState = TrafficState()


class Recieve(threading.Thread):
    def __init__(self, TSlock, PAqueue):
        self.TSlock = TSlock
        self.PAqueue = PAqueue
        threading.Thread.__init__(self)

    def run(self):
        global trafficState

        while True:
            if not self.PAqueue.empty():
                rec = self.PAqueue.get()
                rec = rec[0]
                self.TSlock.acquire()
                if rec[0] == 'P':  # PEDESTRIAN
                    canPass = False
                    # print('[UPR-RECIEVE]: New pedestrian with direction', rec[2:], 'arrived')
                    self.print('[UPR-RECIEVE]: New pedestrian with direction ' + rec[2:] + ' arrived')
                    if rec[2:] == 'SW-SE' or rec[2:] == 'SE-SW' or rec[2:] == 'NW-NE' or rec[2:] == 'NE-NW':
                        if trafficState.SEMstate[5:7] == 'GG':
                            canPass = True
                    if rec[2:] == 'SW-NW' or rec[2:] == 'NW-SW' or rec[2:] == 'SE-NE' or rec[2:] == 'NE-SE':
                        if trafficState.SEMstate[7:] == 'GG':
                            canPass = True
                    if not canPass:
                        trafficState.pedWait[rec[2:]] = True
                if rec[0] == 'C':  # CAR
                    # print('[UPR-RECIEVE]: New car arrived at', rec[2])
                    self.print('[UPR-RECIEVE]: New car arrived at ' + rec[2])
                    canPass = False
                    if rec[2:3] == 'N' or rec[2:3] == 'S':
                        if trafficState.SEMstate[:2] == 'GG':
                            canPass = True
                    if rec[2:3] == 'E' or rec[2:3] == 'W':
                        if trafficState.SEMstate[2:5] == 'GG':
                            canPass = True
                    if not canPass:
                        trafficState.carWait[rec[2:3]] = True
                self.TSlock.release()
            else:
                time.sleep(0.1)

    def print(self, toPrint):
        with open("UPR_RECIEVE.log", 'a') as f:
            f.write(toPrint + '\n')


# NORTH-SOUTH-EAST-WEST
def semCalc(side):
    if side == 'N' or side == 'S':
        return "GGRR-RRGG"
    else:
        return "RRGG-GGRR"


def turnOffPed(curr):
    car, ped = curr.split('-')
    curr = car + '-' + 'RRRR'
    return curr


def turnOffSem():
    return 'RRRR-RRRR'


class State(threading.Thread):
    def __init__(self, TSlock, SEMpipe):
        self.TSlock = TSlock
        self.SEMpipe = SEMpipe
        threading.Thread.__init__(self)

    def run(self):
        global trafficState
        ALL_RED_TIME = 5
        PEDESTRIAN_TIME_OFFSET = 10
        while True:
            self.TSlock.acquire()
            if trafficState.lastSEMstate[0:4] == semCalc('N')[0:4]:
                nextS = 'E'
                self.print('[UPR-STATE]: Next is W-E')
            else:
                nextS = 'N'
                self.print('[UPR-STATE]: Next is N-S')

            if trafficState.isCarWaiting(nextS) or trafficState.isPedWaiting(nextS):
                waitTime = 30
                self.print('[UPR-STATE]: Have someone waiting!')
            else:
                waitTime = 15
                self.print('[UPR-STATE]: No one waiting!')

            trafficState.SEMstate = semCalc(nextS)
            # print(trafficState.SEMstate)
            trafficState.lastSEMstate = trafficState.SEMstate
            self.SEMpipe.send([trafficState.SEMstate, ])
            self.TSlock.release()

            time.sleep(waitTime - PEDESTRIAN_TIME_OFFSET)

            self.TSlock.acquire()
            trafficState.SEMstate = turnOffPed(trafficState.SEMstate)
            self.print('[UPR-STATE]: Turning off pedestrian lights')
            # print(trafficState.SEMstate)
            self.SEMpipe.send([trafficState.SEMstate, ])
            self.TSlock.release()

            time.sleep(PEDESTRIAN_TIME_OFFSET)

            self.TSlock.acquire()
            trafficState.SEMstate = turnOffSem()
            self.print('[UPR-STATE]: Turning off all lights')
            # print(trafficState.SEMstate)
            self.SEMpipe.send([trafficState.SEMstate, ])
            self.TSlock.release()

            time.sleep(ALL_RED_TIME)

    def print(self, toPrint):
        with open("UPR_STATE.log", 'a') as f:
            f.write(toPrint + '\n')


def init(SEMpipe, PAqueue):
    TrafficStateLock = threading.Lock()
    recieveThread = Recieve(TrafficStateLock, PAqueue)
    stateThread = State(TrafficStateLock, SEMpipe)

    recieveThread.start()
    stateThread.start()

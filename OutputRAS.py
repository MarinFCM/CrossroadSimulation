import threading
import time

A = [[' ', ' ', ' ', '|', 'A', '|', ' ', '|', ' ', ' ', ' '],
     [' ', ' ', 'p', '|', ' ', '|', ' ', '|', 'p', ' ', ' '],
     [' ', 'p', ' ', '|', ' ', '|', ' ', '|', ' ', 'p', ' '],
     ['-', '-', '-', '+', ' ', '|', ' ', '+', '-', '-', '-'],
     [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'A'],
     ['-', '-', '-', ' ', ' ', ' ', ' ', ' ', '-', '-', '-'],
     ['A', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
     ['-', '-', '-', '+', ' ', '|', ' ', '+', '-', '-', '-'],
     [' ', 'p', ' ', '|', ' ', '|', ' ', '|', ' ', 'p', ' '],
     [' ', ' ', 'p', '|', ' ', '|', ' ', '|', 'p', ' ', ' '],
     [' ', ' ', ' ', '|', ' ', '|', 'A', '|', ' ', ' ', ' ']]

At = [[' ', ' ', ' ', '|', ' ', '|', ' ', '|', ' ', ' ', ' '],
      [' ', ' ', ' ', '|', ' ', '|', ' ', '|', ' ', ' ', ' '],
      [' ', ' ', ' ', '|', ' ', '|', ' ', '|', ' ', ' ', ' '],
      ['-', '-', '-', '+', ' ', '|', ' ', '+', '-', '-', '-'],
      [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
      ['-', '-', '-', ' ', ' ', ' ', ' ', ' ', '-', '-', '-'],
      [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
      ['-', '-', '-', '+', ' ', '|', ' ', '+', '-', '-', '-'],
      [' ', ' ', ' ', '|', ' ', '|', ' ', '|', ' ', ' ', ' '],
      [' ', ' ', ' ', '|', ' ', '|', ' ', '|', ' ', ' ', ' '],
      [' ', ' ', ' ', '|', ' ', '|', ' ', '|', ' ', ' ', ' ']]


class TrafficState:
    def __init__(self):
        self.carWait = {'N': 0, 'S': 0, 'E': 0, 'W': 0}

        self.carDrive = {'N': 0, 'S': 0, 'E': 0, 'W': 0}

        self.pedWait = {'SW-SE': 0, 'SW-NW': 0, 'SE-SW': 0, 'SE-NE': 0, 'NW-NE': 0, 'NW-SW': 0, 'NE-SE': 0, 'NE-NW': 0}

        self.pedWalk = {'SW-SE': 0, 'SW-NW': 0, 'SE-SW': 0, 'SE-NE': 0, 'NW-NE': 0, 'NW-SW': 0, 'NE-SE': 0, 'NE-NW': 0}


def printRAS():
    out = ""
    for row in At:
        for val in row:
            # print('{}'.format(val), end='')
            out += val
        # print()
        out += '\n'

    with open("RAS.log", 'a') as f:
        f.write(out)


class Recieve(threading.Thread):
    def __init__(self, PAqueue):
        threading.Thread.__init__(self)
        self.PAqueue = PAqueue

    def run(self):
        trafficState = TrafficState()
        while True:
            if not self.PAqueue.empty():
                rec = self.PAqueue.get()
                rec = rec[0]
                if rec[0] == 'P':  # PEDESTRIAN
                    trafficState.pedWait[rec[2:]] += 1
                    if trafficState.pedWait[rec[2:]] == 1:
                        setPed(rec[2:])
                        printRAS()
                if rec[0] == 'C':  # CAR
                    trafficState.carWait[rec[2:]] += 1
                    if trafficState.carWait[rec[2:]] == 1:
                        setCar(rec[2:])
                        printRAS()
                if rec[0] == 'S':  # START
                    if rec[2] == 'P':  # PEDESTRIAN
                        trafficState.pedWait[rec[4:]] -= 1
                        if trafficState.pedWait[rec[4:]] == 0:
                            clearPed(rec[4:])
                        trafficState.pedWalk[rec[4:]] += 1
                        if trafficState.pedWalk[rec[4:]] == 1:
                            fillPed(rec[4:])
                        printRAS()
                    if rec[2] == 'C':  # CAR
                        trafficState.carWait[rec[4:]] -= 1
                        if trafficState.carWait[rec[4:]] == 0:
                            clearCar(rec[4:])
                        trafficState.carDrive[rec[4:]] += 1
                        if trafficState.carDrive[rec[4:]] == 1:
                            fillCars(rec[4:])
                        printRAS()
                if rec[0] == 'D':  # DONE
                    if rec[2] == 'P':  # PEDESTRIAN
                        trafficState.pedWalk[rec[4:]] -= 1
                        if trafficState.pedWalk[rec[4:]] == 0:
                            passedPed(rec[4:])
                            printRAS()
                    if rec[2] == 'C':  # CAR
                        trafficState.carDrive[rec[4:]] -= 1
                        if trafficState.carDrive[rec[4:]] == 0:
                            passedCars(rec[4:])
                            printRAS()
            else:
                time.sleep(0.1)


def init(PAqueue):
    stat = Recieve(PAqueue)
    stat.start()


def fillCars(side):
    if side == 'N':
        for i in range(len(At)):
            At[i][4] = 'A'
    elif side == 'S':
        for i in range(len(At)):
            At[i][6] = 'A'
    elif side == 'W':
        for i in range(len(At[4])):
            At[6][i] = 'A'
    elif side == 'E':
        for i in range(len(At[6])):
            At[4][i] = 'A'


def passedCars(side):
    if side == 'N':
        for i in range(len(At)):
            At[i][4] = ' '
    elif side == 'S':
        for i in range(len(At)):
            At[i][6] = ' '
    elif side == 'W':
        for i in range(len(At[4])):
            At[6][i] = ' '
    elif side == 'E':
        for i in range(len(At[6])):
            At[4][i] = ' '


def setCar(side):
    if side == 'N':
        At[0][4] = 'A'
    elif side == 'S':
        At[10][6] = 'A'
    elif side == 'W':
        At[6][0] = 'A'
    elif side == 'E':
        At[4][10] = 'A'


def clearCar(side):
    if side == 'N':
        At[0][4] = ' '
    elif side == 'S':
        At[10][6] = ' '
    elif side == 'W':
        At[6][0] = ' '
    elif side == 'E':
        At[4][10] = ' '


def fillPed(fromTo):
    if fromTo == 'NW-NE' or fromTo == 'NE-NW':
        At[1][4] = 'p'
        At[1][6] = 'p'
    elif fromTo == 'NE-SE' or fromTo == 'SE-NE':
        At[4][9] = 'p'
        At[6][9] = 'p'
    elif fromTo == 'NW-SW' or fromTo == 'SW-NW':
        At[4][1] = 'p'
        At[6][1] = 'p'
    elif fromTo == 'SW-SE' or fromTo == 'SE-SW':
        At[9][4] = 'p'
        At[9][6] = 'p'


def passedPed(fromTo):
    if fromTo == 'NW-NE' or fromTo == 'NE-NW':
        At[1][4] = ' '
        At[1][6] = ' '
    elif fromTo == 'NE-SE' or fromTo == 'SE-NE':
        At[4][9] = ' '
        At[6][9] = ' '
    elif fromTo == 'NW-SW' or fromTo == 'SW-NW':
        At[4][1] = ' '
        At[6][1] = ' '
    elif fromTo == 'SW-SE' or fromTo == 'SE-SW':
        At[9][4] = ' '
        At[9][6] = ' '


def setPed(fromTo):
    if fromTo == 'NW-NE':
        At[1][2] = 'p'
    elif fromTo == 'NE-NW':
        At[1][8] = 'p'
    elif fromTo == 'NE-SE':
        At[2][9] = 'p'
    elif fromTo == 'SE-NE':
        At[8][9] = 'p'
    elif fromTo == 'NW-SW':
        At[2][1] = 'p'
    elif fromTo == 'SW-NW':
        At[8][1] = 'p'
    elif fromTo == 'SW-SE':
        At[9][2] = 'p'
    elif fromTo == 'SE-SW':
        At[9][8] = 'p'


def clearPed(fromTo):
    if fromTo == 'NW-NE':
        At[1][2] = ' '
    elif fromTo == 'NE-NW':
        At[1][8] = ' '
    elif fromTo == 'NE-SE':
        At[2][9] = ' '
    elif fromTo == 'SE-NE':
        At[8][9] = ' '
    elif fromTo == 'NW-SW':
        At[2][1] = ' '
    elif fromTo == 'SW-NW':
        At[8][1] = ' '
    elif fromTo == 'SW-SE':
        At[9][2] = ' '
    elif fromTo == 'SE-SW':
        At[9][8] = ' '

from multiprocessing import Pipe, Queue
import UPR
import SEM
from GenPC import Car, Pedestrian
import OutputRAS

lst = [
    'P-SW-SE', 'P-SW-NW', 'P-SE-SW', 'P-SE-NE', 'P-NW-NE', 'P-NW-SW',
    'P-NE-SE', 'P-NE-NW', 'C-N', 'C-S', 'C-E', 'C-W']

if __name__ == '__main__':
    SEM_HOST, SEM_PORT = "localhost", 9999
    SEM_Connection = [SEM_HOST, SEM_PORT]
    PipeSEM_UPR1, PipeSEM_UPR2 = Pipe()
    QueuePC_UPR = Queue()
    QueuePC_RAS = Queue()

    UPR.init(PipeSEM_UPR1, QueuePC_UPR)

    SEM.init(PipeSEM_UPR2, SEM_Connection)

    OutputRAS.init(QueuePC_RAS)

    while True:
        tmp = input("Enter new car (eg. C-N) or pedestrian (eg. P-SW-NW)")
        if tmp.strip() not in lst:
            print("Wrong format")
            continue
        else:
            if tmp[0] == 'C':
                Car(tmp[2], QueuePC_UPR, SEM_Connection, QueuePC_RAS).start()
            elif tmp[0] == 'P':
                Pedestrian(tmp[2:], QueuePC_UPR, SEM_Connection, QueuePC_RAS).start()

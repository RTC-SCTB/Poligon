import time
from poligon.cells.elevator import Elevator

elevator = Elevator(host="192.168.255.1", invfreq=0.1)
elevator.start()

while True:
    time.sleep(1)

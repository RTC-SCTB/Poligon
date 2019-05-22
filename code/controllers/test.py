from controllers.et_7060 import ET_7060
import time

controller = ET_7060('192.168.255.1')


while True:
    controller.Relay1 = True
    print(controller.Relay1)

    time.sleep(2)

    controller.Relay1 = False
    print(controller.Relay1)

    time.sleep(2)
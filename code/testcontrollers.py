from controllers.et_7060 import ET_7060
import time

controller = ET_7060('192.168.255.1')


while True:
    controller.Relay0 = True
    print(controller.Relay1)
    print(controller.DI0, controller.DI1, controller.DI2, controller.DI3)
    time.sleep(1)

    controller.Relay0 = False
    print(controller.Relay1)

    time.sleep(1)

import os
import random
from threading import Thread
from time import sleep

class Sensor:
    unit = os.getenv("S_UNIT", "C")
    min = float(os.getenv("S_MIN", 0))
    max = float(os.getenv("S_MAX", 30))
    step = float(os.getenv("S_STEP", 0.5))
    interval = float(os.getenv("S_INT", 1))
    active = False

    def __run(self):
        while (self.active):
            sleep(self.interval)
            val = round(random.uniform(self.min, self.max) / self.step) * self.step
            print(val)

    def start(self):
        print("starting")
        if (self.active == False):
            self.active = True
            self.__thread = Thread(target=self.__run)
            self.__thread.start()

    def stop(self):
        print("stopping")
        if (self.active == True):
            self.active = False
            self.__thread.join()

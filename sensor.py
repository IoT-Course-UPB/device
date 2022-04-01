import os
import random
import datetime
import json
from threading import Thread, Lock
from time import sleep


class Sensor:
    metric = os.getenv("S_METRIC", "temperature")
    unit = os.getenv("S_UNIT", "C")
    min = float(os.getenv("S_MIN", 0))
    max = float(os.getenv("S_MAX", 30))
    step = float(os.getenv("S_STEP", 0.5))
    interval = float(os.getenv("S_INT", 1))
    name = str(os.getenv("D_NAME")) + '_s'
    last_sample = {}
    mutex = Lock()
    active = False

    def __run(self):
        while (self.active):
            sleep(self.interval)
            json = self.__generate_payload()
            #print(json)

    def start(self):
        if (self.active == False):
            print("Sensor of device " + self.name + " starting")
            self.active = True
            self.__generate_payload()
            self.__thread = Thread(target=self.__run)
            self.__thread.start()
        else:
            print("Sensor of device " + self.name + " already started")

    def stop(self):
        if (self.active == True):
            print("Sensor of device " + self.name + " stopping")
            self.active = False
            self.__generate_payload()
            self.__thread.join()
        else:
            print("Sensor of device " + self.name + " already stopped")

    def __generate_payload(self):
        val = round(random.uniform(self.min, self.max) / self.step) * self.step
        data = {'name': self.name, 'timestamp': str(datetime.datetime.now(
        )), self.metric: val, 'unit': self.unit, 'active': self.active}

        self.__set_last_sample(data)

        return json.dumps(data)

    def __set_last_sample(self, sample):
        self.mutex.acquire()
        self.last_sample = sample
        self.mutex.release()

    def get_last_sample(self):
        self.mutex.acquire()
        sample = self.last_sample
        self.mutex.release()
        return sample

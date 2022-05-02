import os
import random
import datetime
import json
import sys
import pika
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

    def __send_data_to_server(self, data):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='rabbitmq'))
        channel = connection.channel()
        channel.queue_declare(queue='data_queue', durable=True)
        channel.basic_publish(
            exchange='',
            routing_key='data_queue',
            body=data,
            properties=pika.BasicProperties(
                delivery_mode=2,
            ))
        connection.close()

    def __run(self):
        while (self.active):
            sleep(self.interval)
            json = self.__generate_payload()
            print("Sensor " + self.name + " generated data: " + json)
            self.__send_data_to_server(json)
            sys.stdout.flush()

    def start(self):
        if (self.active == False):
            print("Sensor " + self.name + " starting")
            self.active = True
            self.__generate_payload()
            self.__thread = Thread(target=self.__run)
            self.__thread.start()
        else:
            print("Sensor " + self.name + " already started")

    def stop(self):
        if (self.active == True):
            print("Sensor " + self.name + " stopping")
            self.active = False
            self.__generate_payload()
            self.__thread.join()
        else:
            print("Sensor " + self.name + " already stopped")

    def __generate_payload(self):
        val = round(random.uniform(self.min, self.max) / self.step) * self.step
        data = {'name': self.name, 'timestamp': str(datetime.datetime.now(
        )), 'measurement': val, 'metric': self.metric, 'unit': self.unit, 'active': self.active}

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

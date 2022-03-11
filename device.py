from pickle import TRUE
from re import S
from time import sleep
from flask import Flask, jsonify
from actuator import Actuator
from sensor import Sensor
from enum import Enum
import os


class DeviceType(Enum):
    SENSOR = 1
    ACTUATOR = 2
    BOTH = 3


app = Flask(__name__)

# D_NAME
name = os.getenv("D_NAME")
if name == None:
    raise RuntimeError("Name not set")

# D_TYPE
type = os.getenv("D_TYPE", DeviceType.BOTH)

# D_DESC
description = os.getenv("D_DESC", "")

print("Name: " + name + ", Type: " + str(type) + ", Description: " + description)

sensor = Sensor()
actuator = Actuator()

if (type == DeviceType.BOTH):
    sensor.start()
    actuator.start()
elif (type == DeviceType.SENSOR):
    sensor.start()
else:
    actuator.start()


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/start")
def start():
    print("Start")
    sensor.start()
    return jsonify(status="started")


@app.route("/stop")
def stop():
    print("Stop")
    sensor.stop()
    return "<p>Hello, World!</p>"

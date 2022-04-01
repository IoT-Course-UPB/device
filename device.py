from pickle import TRUE
from re import S
from time import sleep
from flask import Flask, Response, jsonify, render_template, request
from actuator import Actuator
from sensor import Sensor
import json
from enum import Enum
import os


def start_all():
    if (type == DeviceType.BOTH):
        sensor.start()
        actuator.start()
    elif (type == DeviceType.SENSOR):
        sensor.start()
    else:
        actuator.start()


def stop_all():
    if (type == DeviceType.BOTH):
        sensor.stop()
        actuator.stop()
    elif (type == DeviceType.SENSOR):
        sensor.stop()
    else:
        actuator.stop()


def get_status():
    if (type == DeviceType.BOTH):
        return {"name": name, "description": description, "sensor": sensor.get_last_sample(),
                "actuator": actuator.get_status()}
    elif (type == DeviceType.SENSOR):
        return {"name": name, "description": description, "sensor": sensor.get_last_sample()}
    else:
        return {"name": name, "description": description, "actuator": actuator.get_status()}


def get_status_sensor():
    return {"name": name, "description": description, "sensor": sensor.get_last_sample()}


def get_status_actuator():
    return {"name": name, "description": description, "actuator": actuator.get_status()}


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

start_all()


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/start")
def start():
    print("Starting component(s) of device" + name)
    start_all()
    return jsonify(get_status())


@app.route("/stop")
def stop():
    print("Stopping component(s) of device" + name)
    stop_all()
    return jsonify(get_status())


@app.route("/start_sensor")
def start_sensor():
    print("Starting sensor of device" + name)
    sensor.start()
    return jsonify(get_status())


@app.route("/stop_sensor")
def stop_sensor():
    print("Stopping sensor of device" + name)
    sensor.stop()
    return jsonify(get_status())


@app.route("/start_actuator")
def start_actuator():
    print("Starting actuator of device" + name)
    actuator.start()
    return jsonify(get_status())


@app.route("/stop_actuator")
def stop_actuator():
    print("Stopping actuator of device" + name)
    actuator.stop()
    return jsonify(get_status())


@app.route("/status")
def status():
    return jsonify(get_status())


@app.route("/status_view")
def status_view():
    if (sensor.active == True):
        sensor_status = "active"
    else:
        sensor_status = "inactive"

    if (actuator.active == True):
        actuator_status = "active"
    else:
        actuator_status = "inactive"

    sample = sensor.get_last_sample()

    if (type == DeviceType.BOTH):
        return render_template("status.html",
                               name=name,
                               description=description,
                               has_sensor=True,
                               sensor_name=sensor.name,
                               sensor_status=sensor_status,
                               sensor_timestamp=sample.get("timestamp"),
                               sensor_metric=sensor.metric.title(),
                               sensor_value=sample.get(sensor.metric),
                               sensor_unit=sample.get("unit"),
                               has_actuator=True,
                               actuator_name=actuator.name,
                               actuator_status=actuator_status,
                               actuator_state=actuator.state,
                               actuator_unit=actuator.unit
                               )
    elif (type == DeviceType.SENSOR):
        return render_template("status.html",
                               name=name,
                               description=description,
                               has_sensor=True,
                               sensor_name=sensor.name,
                               sensor_status=sensor_status,
                               sensor_timestamp=sample.get("timestamp"),
                               sensor_metric=sensor.metric.title(),
                               sensor_value=sample.get(sensor.metric),
                               sensor_unit=sample.get("unit"),
                               has_actuator=False
                               )
    else:
        return render_template("status.html",
                               name=name,
                               description=description,
                               has_sensor=False,
                               has_actuator=True,
                               actuator_name=actuator.name,
                               actuator_status=actuator_status,
                               actuator_state=actuator.state,
                               actuator_unit=actuator.unit
                               )


@app.route("/status_sensor")
def status_sensor():
    return jsonify(get_status_sensor())


@app.route("/status_actuator")
def status_actuator():
    return jsonify(get_status_actuator())


@app.route("/set_actuator", methods=['POST'])
def set_actuator():
    if (actuator.set_state(request.form["state"]) == False):
        return Response(json.dumps({"error": "invalid state parameter"}), status=400, mimetype='application/json')
    return jsonify(get_status_actuator())


if __name__ == "__main__":
    app.run(host="0.0.0.0")

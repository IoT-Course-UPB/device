from time import sleep
from flask import Flask, Response, jsonify, render_template, request
from actuator import Actuator
from sensor import Sensor
import json
import pika
from enum import Enum
from threading import Thread
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


def connect_to_server(name):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue=name, durable=True)
    return channel


def try_to_connect_to_server(name):
    try:
        channel = connect_to_server(name)
        return channel
    except:
        sleep(1)
        channel = try_to_connect_to_server(name)
        return channel


def send_update_to_server():
    info = json.dumps(get_status())

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='device_queue', durable=True)
    channel.basic_publish(
        exchange='',
        routing_key='device_queue',
        body=info,
        properties=pika.BasicProperties(
            delivery_mode=2,
        ))
    connection.close()


def subscriber_thread_function(channel):
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=name,
                          on_message_callback=server_message_callback)
    channel.start_consuming()


def server_message_callback(ch, method, properties, body):
    cmd = body.decode()
    print("Received from server: %s" % cmd)
    ch.basic_ack(delivery_tag=method.delivery_tag)


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
if (type != DeviceType.BOTH):
    if (type == "1"):
        type = DeviceType.SENSOR
    elif (type == "2"):
        type = DeviceType.ACTUATOR
    else:
        type = DeviceType.BOTH

# D_DESC
description = os.getenv("D_DESC", "")

print("Name: " + name + ", Type: " + str(type) + ", Description: " + description)

print("Connecting to queue...")

channel = try_to_connect_to_server(name)

print("Connected to queue")

# start thread that listens to commands from the server
subscriber_thread = Thread(target=subscriber_thread_function, args=(channel,))
subscriber_thread.start()

sensor = Sensor()
actuator = Actuator()

start_all()

send_update_to_server()


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/start", methods=['POST'])
def start():
    print("Starting component(s) of device " + name)
    start_all()
    send_update_to_server()
    return jsonify(get_status())


@app.route("/stop", methods=['POST'])
def stop():
    print("Stopping component(s) of device " + name)
    stop_all()
    send_update_to_server()
    return jsonify(get_status())


@app.route("/start_sensor", methods=['POST'])
def start_sensor():
    print("Starting sensor of device" + name)
    sensor.start()
    send_update_to_server()
    return jsonify(get_status())


@app.route("/stop_sensor", methods=['POST'])
def stop_sensor():
    print("Stopping sensor of device " + name)
    sensor.stop()
    send_update_to_server()
    return jsonify(get_status())


@app.route("/start_actuator", methods=['POST'])
def start_actuator():
    print("Starting actuator of device " + name)
    actuator.start()
    send_update_to_server()
    return jsonify(get_status())


@app.route("/stop_actuator", methods=['POST'])
def stop_actuator():
    print("Stopping actuator of device " + name)
    actuator.stop()
    send_update_to_server()
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
    state = request.form["state"]
    if (actuator.active == False):
        return Response(json.dumps({"error": "actuator not active"}), status=400, mimetype='application/json')

    if (actuator.set_state(state) == False):
        return Response(json.dumps({"error": "invalid state parameter"}), status=400, mimetype='application/json')

    send_update_to_server()
    return jsonify(get_status_actuator())


if __name__ == "__main__":
    app.run(host="0.0.0.0")

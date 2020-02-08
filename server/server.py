import json
from flask import Flask, request

import enum
from typing import NamedTuple

app = Flask(__name__)

# TODO - use data base instead
data = {}

# data structs

class State(enum.Enum):
    new = 0   # got into range
    probe = 1 # still within range
    lost = 2  # out of range

def get_state_name(state):
    return State[state].name

class DeviceLog(NamedTuple):
    time: int
    state: State
    strength: int

def encode_devicelog(log):
    return {"time": log.time,
            "state": get_state_name(log.state),
            "strength": log.strength}

class MacEntry(NamedTuple):
    name: str
    logs: list

def encode_entry(e):
    return {"name": e.name,
            "logs": [encode_devicelog(log) for log in e.logs]}

# data logic

def make_log(json_entry):
    time = json_entry["time"]
    state = json_entry["state"]
    strength = json_entry["strength"]
    return DeviceLog(time, state, strength)

def make_mac_entry(json_entry):
    name = json_entry["name"]
    logs = []
    return MacEntry(name, logs)

def get_mac_entry(json_entry):
    print(json_entry)
    entry_mac = json_entry["entry"] # get mac address
    if entry_mac in data:
        encoded_entry = encode_entry(data[entry_mac])
        print(encoded_entry)
        return encoded_entry
    return "nope"

def add_sniff_data(json_data):
    for entry in json_data:
        mac = entry["mac"]
        new_log = make_log(entry)
        if not mac in data:
            data[mac] = make_mac_entry(entry)
        data[mac].logs.append(new_log)

# server main logic

@app.route('/')
def index():
    return 'Hello world'

@app.route("/node", methods=["POST"])
def nodePostHandler():
    if len(request.data) == 0:
        return "Malformated query request"

    try:
        json_data = json.loads(request.data)
    except ValueError as e:
        print("bad data")
        return "Malformated json request"

    print(json_data)

    add_sniff_data(json_data)
    return "added entries"

@app.route("/node", methods=["GET"])
def nodeGetHandler():
    if len(request.data) == 0:
        return "Malformated query request"

    try:
        json_data = json.loads(request.data)
    except ValueError as e:
        return "Malformated json request"
    return get_mac_entry(json_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

import json
from flask import Flask, request

import enum
from typing import NamedTuple

app = Flask(__name__)

# TODO - use data base instead
data = []

# data logic

def make_log(json_entry):
    time = json_entry["time"]
    strength = json_entry["strength"]
    return {'time': time, 'strength': strength}

def make_mac_entry(json_entry):
    mac = json_entry['mac']
    name = json_entry["name"]
    return {"name": name, "logs": []}

def get_mac_entry(json_entry):
    print(json_entry)
    # entry_mac = json_entry["entry"] # get mac address
    return "nope"

def add_sniff_data(json_data):
    new_frame = {}
    for entry in json_data:
        mac = entry["mac"]
        new_log = make_log(entry)
        if not (mac in new_frame):
            new_frame[mac] = make_mac_entry(entry)
        new_frame[mac].logs.append(new_log)
    data.append(new_frame)

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
    except ValueError:
        return "(POST) Malformated json request"

    print(json_data)

    add_sniff_data(json_data)
    return "added entries"

@app.route("/node", methods=["GET"])
def nodeGetHandler():
    return {'data': data}
    # if len(request.data) == 0:
    #     return "(GET) Malformated query request"

    # try:
    #     json_data = json.loads(request.data)
    # except ValueError:
    #     return "Malformated json request"
    # return get_mac_entry(json_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

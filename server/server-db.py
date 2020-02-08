
import json
from flask import Flask, request
from flask_cors import CORS

import enum
from typing import NamedTuple
from tinydb import TinyDB, Query

# global vars

db = TinyDB("data.json")
app = Flask(__name__)

CORS(app)

# data structs

class State(enum.Enum):
    new = 0   # got into range
    probe = 1 # still within range
    lost = 2  # out of range

def get_state_name(state):
    return State[state].name

# db op

def find_mac_in_db(db, json_query):
    entry = Query()
    if "mac" in json_query:
        mac = json_query["mac"] # get mac address
        return db.search(entry.mac == mac)
    elif "name" in json_query:
        name = json_query["name"] # get mac address
        return db.search(entry.name == name)
    return db.search(entry.mac.test(lambda e: True))


def reset_db(db):
    entry = Query()
    db.remove(entry.name)

# data logic

def make_log(json_entry):
    time = json_entry["time"]
    state = json_entry["state"]
    strength = json_entry["strength"]
    return {"time": time, "state": state, "strength": strength}

def make_mac_entry(json_entry):
    mac = json_entry["mac"]
    name = json_entry["name"]
    logs = []
    return {"mac": mac, "name": name, "logs": logs}

def get_mac_entries(json_query):
    print(json_query)
    matches = find_mac_in_db(db, json_query)
    if matches:
        print(matches)
        return matches
    return "no match"


def add_sniff_data(json_data):
    entry_query = Query()
    print(json_data)
    for entry in json_data:
        new_log = make_log(entry)
        matches = find_mac_in_db(db, entry)
        if not matches:
            new_entry = make_mac_entry(entry)
            print(new_entry)
            new_entry['logs'].append(new_log)
            db.insert(new_entry)
        else:
            entry = matches[0]
            print(entry)
            entry['logs'].append(new_log)
            db.write_back(matches)

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
        return "Malformated json request"

    add_sniff_data(json_data)
    return "added entries"

@app.route("/node", methods=["GET"])
def nodeGetHandler():
    # if len(request.data) == 0:
    #     return "Malformated query request"

    # try:
    #     json_data = json.loads(request.data)
    # except ValueError as e:
    #     return "Malformated json request"
    json_data = {}
    return {"data": get_mac_entries(json_data)}

if __name__ == '__main__':
    reset_db(db)
    app.run(debug=True, host='0.0.0.0')

import json
from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# TODO - use data base instead
data = []

# data logic

def make_mac_entry(json_entry):
    mac = json_entry['mac']
    name = json_entry["name"]
    time = json_entry["time"]
    strength = json_entry["strength"]
    return {'mac': mac, 'name': name, 'time': time, 'strength': strength}

def get_mac_entry(json_entry):
    print(json_entry)
    # entry_mac = json_entry["entry"] # get mac address
    return "nope"

def add_sniff_data(json_data):
    new_frame = [make_mac_entry(entry) for entry in json_data]
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
    data = {}
    with open("formatted.json") as json_file:
        data = json.load(json_file)
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

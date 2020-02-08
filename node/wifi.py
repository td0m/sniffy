from scapy.all import *
import threading
import requests
import time
import json

endpoint = "http://10.14.138.32:5000/node"

devices = []

def PacketHandler(pkt):
    if pkt.haslayer(Dot11):
        # type 0 checks for management frame
        # subtype 4 checks for probe request
        # subtype 8 for beacons
        if pkt.type == 0 and pkt.subtype == 4:
            if pkt.addr2 not in devices:
                signal = pkt.getfieldval('dBm_AntSignal')
                devices.append({
                    "state": "new",
                    "time": time.time(),
                    "mac": pkt.addr2,
                    "name": pkt.info.decode("utf-8"),
                    "strength": signal
                })

def upload_periodically():
    while True:
        global devices
        data = devices
        print(data)
        try:
            r = requests.post(url = endpoint, json = data)
            print(r.text)
        except Exception as e:
            print(e)

        with open('data.json', 'w') as outfile:
            json.dump(devices, outfile, indent=2)
        time.sleep(7)

upload_thread = threading.Thread(target=upload_periodically)
upload_thread.start()

sniff(iface="wlp0s20f0u1", prn = PacketHandler)

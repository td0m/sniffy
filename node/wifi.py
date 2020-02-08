from scapy.all import *
import threading
import requests
import time
import json
from mac_vendor_lookup import MacLookup

endpoint = "http://10.14.138.32:5000/node"

devices = []
allTime = []

unique = []

lookup = MacLookup()

def PacketHandler(pkt):
    if pkt.haslayer(Dot11):
        # type 0 checks for management frame
        # subtype 4 checks for probe request
        # subtype 8 for beacons
        if pkt.type == 0 and pkt.subtype == 4:
            if pkt.addr2 not in devices:
                signal = pkt.getfieldval('dBm_AntSignal')
                if pkt.addr2 not in unique:
                    manufacturer = "-"
                    try:
                        manufacturer = lookup.lookup(pkt.addr2)
                        unique.append(pkt.addr2)
                        devices.append({
                            "state": "new",
                            "time": time.time(),
                            "mac": pkt.addr2,
                            #"name": pkt.info.decode("utf-8"),
                            "name": manufacturer,
                            "strength": signal
                        })
                        print(f"size: {len(unique)}, device: {pkt.addr2}, manufacturer: {manufacturer}")
                    except Exception:
                        # yay
                        print("")
                        

def upload_periodically():
    while True:
        global devices
        global allTime
        data = devices
        allTime = allTime + devices
        try:
            r = requests.post(url = endpoint, json = data)
            print("")
        except Exception as e:
            print(e)

        devices = []

        with open('data.json', 'w') as outfile:
            json.dump(allTime, outfile, indent=2)
        time.sleep(20)

upload_thread = threading.Thread(target=upload_periodically)
upload_thread.start()

sniff(iface="wlp0s20f0u1", prn = PacketHandler)

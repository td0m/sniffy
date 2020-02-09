from scapy.all import *
import threading
import requests
import time
import json
import math
from mac_vendor_lookup import MacLookup

endpoint = "http://10.14.138.32:5000/node"

devices = []
allTime = []

startTime = time.time()

lookup = MacLookup()

frameId = 0

def shouldAppend(mac):
    for d in devices:
        if d["mac"] == mac:
            return False
    return True

oftenUsed = [
  "huawei",
  "samsung",
  "apple",
  "motorola",
  "oneplus",
  "tp-link",
  "xiaomi",
  "d-link",
  "amazon",
  "lenovo",
  "intel",
  "microsoft",
  "espressif",
  "hmd",
  "lg",
  "compal",
  "cybertan",
  "azurewave"
  ]

def formatName(name):
    lowerName = name.lower()
    firstWord = lowerName.split(" ")[0]
    if firstWord == "murata":
        return "Samsung"

    if firstWord in oftenUsed:
        return name.split(" ")[0]
    
    return " ".join(name.split(" ")[0:2])

def PacketHandler(pkt):
    if pkt.haslayer(Dot11):
        # type 0 checks for management frame
        # subtype 4 checks for probe request
        # subtype 8 for beacons
        if pkt.type == 0 and pkt.subtype == 4:
            if pkt.addr2 not in devices:
                signal = pkt.getfieldval('dBm_AntSignal')
                manufacturer = "-"
                try:
                    manufacturer = lookup.lookup(pkt.addr2)
                    if shouldAppend(pkt.addr2):
                        devices.append({
                            "time": time.time(),
                            "mac": pkt.addr2,
                            #"name": pkt.info.decode("utf-8"),
                            "name": formatName(manufacturer),
                            "strength": signal,
                        })
                        print(f"[{frameId}]: {pkt.addr2}")
                except Exception as e:
                    x=1
                    print(e)

def upload_periodically():
    while True:
        time.sleep(60 * 1)
        global frameId
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

        with open(f"data{round(startTime)}.json", 'w') as outfile:
            json.dump(allTime, outfile, indent=2)
        frameId += 1

upload_thread = threading.Thread(target=upload_periodically)
upload_thread.start()

print("sniffing")
sniff(iface="wlp0s20f0u1", prn = PacketHandler)

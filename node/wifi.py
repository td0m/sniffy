from scapy.all import *

devices = []

def PacketHandler(pkt):
    if pkt.haslayer(Dot11):
        if pkt.type == 0 and pkt.subtype == 8:
            print(f"MAC: {pkt.addr2} {str(pkt.info)}")

sniff(iface="wlp0s20f0u1", prn = PacketHandler)

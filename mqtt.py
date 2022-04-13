# Smart Meter GPS decoding script
# @BitBangingBytes
#
# Dumps data to console, copy and paste to a file and save as .csv
#
from base64 import decode
import socket
import select
import string
import sys
import binascii
import struct
import time
import os
# import numpy as np

# main function
if __name__ == "__main__":

    if(len(sys.argv) < 3):
        print('Usage python SmartMeterGPSDecoder-v1.py hostname port')
        sys.exit()

    sdrHost = sys.argv[1]
    sdrPort = int(sys.argv[2])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    # connect to remote host
    try:
        s.connect_ex((sdrHost, sdrPort))
    except:
        print('Unable to connect to flowgraph')
        sys.exit()
    print('Connected to remote SDR flowgraph')
    meter1ID = os.environ.get('Meter1_ID')
    mqttHost = os.environ.get('MQTT_Broker')
    mqttPort = os.environ.get('MQTT_Port')
    mqttUser = os.environ.get('MQTT_User')
    mqttPass = os.environ.get('MQTT_Password')
    
    os.system(
        'mosquitto_pub -r -h {h} -u {u} -P "{p}" -t homeassistant/sensor/electric_meter/uptime/config -m {m}'.format(h=mqttHost, u=mqttUser, p=mqttPass, m='\'{"name": "Electric Meter Uptime", "uniq_id": "METERelectric_2", "state_topic": "meters/electric/uptime/state"}\''))

    os.system(
        'mosquitto_pub -r -h {h} -u {u} -P "{p}" -t homeassistant/sensor/electric_meter/raw/config -m {m}'.format(h=mqttHost, u=mqttUser, p=mqttPass, m='\'{"name": "Electric Meter Raw", "uniq_id": "METERelectric_3", "state_topic": "meters/electric/raw/state"}\''))

    os.system(
        'mosquitto_pub -r -h {h} -u {u} -P "{p}" -t homeassistant/sensor/electric_meter/meterid/config -m {m}'.format(h=mqttHost, u=mqttUser, p=mqttPass, m='\'{"name": "Electric Meter ID", "uniq_id": "METERelectric_4", "state_topic": "meters/electric/meterid/state"}\''))

    os.system(
        'mosquitto_pub -r -h {h} -u {u} -P "{p}" -t homeassistant/sensor/electric_meter/d5/config -m {m}'.format(h=mqttHost, u=mqttUser, p=mqttPass, m='\'{"name": "Electric Meter D5", "uniq_id": "METERelectric_5", "state_topic": "meters/electric/d5/state"}\''))

    while 1:
        sdr_socket_list = [sys.stdin, s]

        # Get the list sockets which are readable
        sdr_read_sockets, sdr_write_sockets, sdr_error_sockets = select.select(
            sdr_socket_list, [], [])

        for sock in sdr_read_sockets:
            # incoming message from remote server
            if sock == s:
                sdrData = sock.recv(4096)
                if not sdrData:
                    print('Connection closed')
                    sys.exit()
                else:
                    # print("The original string is : " + str(sdrData))
                    # Do nothing for the Non-GPS data
                    # Non-GPS Routed Data
                    if ((binascii.hexlify(bytearray(sdrData[3])) == "55") and (binascii.hexlify(bytearray(sdrData[13])) == "fe")):
                        upTime = int(binascii.hexlify(
                            bytearray(sdrData[20:24])), 16)
                        meterID = bytearray(sdrData[26:30])
                        print(binascii.hexlify(meterID).upper() + "," +
                              str(upTime) + "," + str(upTime/60/60/24))
                        os.system('mosquitto_pub -h {h} -u {u} -P "{p}" -t meters/electric/uptime/state -m "{m}"'.format(
                            h=mqttHost, u=mqttUser, p=mqttPass, m=upTime))
                        os.system(
                            'mosquitto_pub -h {h} -u {u} -P "{p}" -t meters/electric/raw/state -m "{m}"'.format(
                                h=mqttHost, u=mqttUser, p=mqttPass, m=binascii.hexlify(sdrData)))
                        os.system('mosquitto_pub -h {h} -u {u} -P "{p}" -t meters/electric/meterid/state -m "{m}"'.format(
                            h=mqttHost, u=mqttUser, p=mqttPass, m=binascii.hexlify(meterID).upper()))
                    else:
                        print('Message D5: {}'.format(
                            binascii.hexlify(sdrData)))
                        os.system(
                            'mosquitto_pub -h {h} -u {u} -P "{p}" -t meters/electric/d5/state -m "{m}"'.format(
                                h=mqttHost, u=mqttUser, p=mqttPass, m=binascii.hexlify(sdrData)))
            else:
                msg = sys.stdin.readline()
                s.send(msg)

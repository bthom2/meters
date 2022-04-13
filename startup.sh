#!/bin/bash

echo "export MQTT_Password=$MQTT_Password" >> /root/.bashrc
echo "export MQTT_User=$MQTT_User" >> /root/.bashrc
echo "export MQTT_Broker=$MQTT_Broker" >> /root/.bashrc
echo "export MQTT_Port=$MQTT_Port" >> /root/.bashrc
echo "export Meter1_ID=$Meter1_ID" >> /root/.bashrc
echo "export Meter1_CRC=$Meter1_CRC" >> /root/.bashrc
echo "export PYTHONPATH=$PYTHONPATH" >> /root/.bashrc
echo "export DISPLAY=$DISPLAY" >> /root/.bashrc

(cd /opt/meters && exec git pull origin master)

exec python2.7 /opt/meters/mqtt.py

service ssh start
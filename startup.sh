#!/bin/bash

echo "export MQTT_Password=$MQTT_Password" >> /root/.bashrc
echo "export MQTT_User=$MQTT_User" >> /root/.bashrc
echo "export MQTT_Broker=$MQTT_Broker" >> /root/.bashrc
echo "export MQTT_Port=$MQTT_Port" >> /root/.bashrc
echo "export Meter1_ID=$Meter1_ID" >> /root/.bashrc
echo "export Meter1_CRC=$Meter1_CRC" >> /root/.bashrc
echo "export PYTHONPATH=$PYTHONPATH" >> /root/.bashrc
echo "export DISPLAY=$DISPLAY" >> /root/.bashrc

(cd /opt/meters && exec git reset --hard HEAD)
(cd /opt/meters && exec git pull)
chmod +x /opt/meters/startup.sh

service ssh start

python3 /opt/meters/fhss_detector_reference_rtlsdr.py 
sleep 10
python2.7 /opt/meters/mqtt.py 127.0.0.1 5002 


# Smart Meter GPS decoding script
# @BitBangingBytes
#
# Dumps data to console, copy and paste to a file and save as .csv
#
from base64 import decode
import socket, select, string, sys, binascii, struct, time, os
# import numpy as np

#main function
if __name__ == "__main__":
	
	if(len(sys.argv) < 3) :
		print('Usage python SmartMeterGPSDecoder-v1.py hostname port')
		sys.exit()
	
	sdrHost = sys.argv[1]
	sdrPort = int(sys.argv[2])

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(2)
	# connect to remote host
	try :
		s.connect_ex((sdrHost, sdrPort))
	except :
		print('Unable to connect to flowgraph')
		sys.exit()
	print ('Connected to remote SDR flowgraph')

	while 1:
		sdr_socket_list = [sys.stdin, s]
		
		# Get the list sockets which are readable
		sdr_read_sockets, sdr_write_sockets, sdr_error_sockets = select.select(sdr_socket_list , [], [])
		
		for sock in sdr_read_sockets:
			#incoming message from remote server
			if sock == s:
				sdrData = sock.recv(4096)
				if not sdrData :
					print ('Connection closed')
					sys.exit()
				else :
					#print("The original string is : " + str(sdrData))
					#Do nothing for the Non-GPS data
					if ((binascii.hexlify(bytearray(sdrData[3])) == "55") and (binascii.hexlify(bytearray(sdrData[13])) == "fe")) : #Non-GPS Routed Data
						upTime = int(binascii.hexlify(bytearray(sdrData[20:24])),16)
						meterID = bytearray(sdrData[26:30])
						print (binascii.hexlify(meterID).upper() + "," + str(upTime) + "," + str(upTime/60/60/24))
						os.system('mosquitto_pub --topic meters/electric/uptime/state --message "{}"'.format(upTime))
						os.system('mosquitto_pub --topic meters/electric/raw/state --message "{}"'.format(binascii.hexlify(sdrData)))
						os.system('mosquitto_pub --topic meters/electric/meterID --message "{}"'.format(binascii.hexlify(meterID).upper()))
					else :
						print('Message D5: {}'.format(binascii.hexlify(sdrData)))
						os.system('mosquitto_pub --topic meters/electric/raw/D5/state --message "{}"'.format(binascii.hexlify(sdrData)))
			else :
				msg = sys.stdin.readline()
				s.send(msg)



# docker run --name mcrelay -it --rm -v relay:/var/run/relay -v $(pwd)/source/mcrelay.py:/mcrelay.py python:latest python /mcrelay.py

import os, socket, threading, json

os.remove( "/var/run/relay/minecraft.sock" )

relaySocket = socket.socket( socket.AF_UNIX, socket.SOCK_DGRAM )
relaySocket.bind( "/var/run/relay/minecraft.sock" )
os.chmod( "/var/run/relay/minecraft.sock", 0o777 )

def receiveData():
	global relaySocket

	while True:
		data, sender = relaySocket.recvfrom( 1024 )
		print( sender, data.decode() )
		relaySocket.sendto( json.dumps( { "type": 0, "status": 0, "data": {} } ).encode(), sender )

receiveThread = threading.Thread( target = receiveData )
receiveThread.start()

while True:
	msg = input()
	relaySocket.sendto( msg.encode(), "/var/run/relay/discordbot.sock" )

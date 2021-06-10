import os, socket, enum, functools, json

_SOCKET_PATH_FORMAT = "/var/run/relay/{0}.sock"

_relaySocket = socket.socket( socket.AF_UNIX, socket.SOCK_DGRAM )
_myPath = None
_eventLoop = None

class Status( enum.Enum ):
	Success = 0
	Error = 1

class Type( enum.Enum ):
	Response = 0
	Status = 1
	Message = 2
	Command = 3

def Setup( myName, eventLoop ):
	global _myPath, _eventLoop, _relaySocket

	_myPath = _SOCKET_PATH_FORMAT.format( myName )
	_eventLoop = eventLoop

	_relaySocket.bind( _myPath )
	_relaySocket.settimeout( 1.0 )

	os.chmod( _myPath, 0o777 )

async def Send( typeOfPayload, payloadData, destinationName ):
	global _relaySocket

	dataToSend = json.dumps( {
		"type": typeOfPayload.value,
		"data": payloadData
	} ).encode()

	await _eventLoop.run_in_executor( None, functools.partial( _relaySocket.sendto, dataToSend, _SOCKET_PATH_FORMAT.format( destinationName ) ) )

	receivedData, sourcePath = await _eventLoop.run_in_executor( None, functools.partial( _relaySocket.recvfrom, 1024 ) )
	receivedPayload = json.loads( receivedData.decode() )

	if receivedPayload[ "type" ] != Type.Response.value:
		raise Exception( "Received non-response ({0}) data from: {1}".format( receivedPayload[ "type" ], sourcePath ) )

	if receivedPayload[ "status" ] != Status.Success.value:
		raise Exception( "Received non-success ({0}) response from: {1}".format( receivedPayload[ "status" ], sourcePath ) )

	return receivedPayload[ "data" ]

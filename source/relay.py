import os, socket, enum, functools, json, asyncio

_SOCKET_PATH_FORMAT = "/var/run/relay/{0}.sock"

_relaySocket = socket.socket( socket.AF_UNIX, socket.SOCK_DGRAM )
_myPath = None

class status( enum.Enum ):
	success = 0
	error = 1

class type( enum.Enum ):
	response = 0
	status = 1
	message = 2
	command = 3

def setup( myName ):
	_myPath = _SOCKET_PATH_FORMAT.format( myName )

	_relaySocket.bind( _myPath )
	_relaySocket.settimeout( 1.0 )

	os.chmod( _myPath, 0o777 )

def cleanup():
	if os.path.exists( _myPath ):
		os.remove( _myPath )

async def send( typeOfPayload, payloadData, destinationName ):
	dataToSend = json.dumps( {
		"type": typeOfPayload.value,
		"data": payloadData
	} ).encode()

	eventLoop = asyncio.get_event_loop()

	await eventLoop.run_in_executor( None, functools.partial( _relaySocket.sendto, dataToSend, _SOCKET_PATH_FORMAT.format( destinationName ) ) )

	receivedData, sourcePath = await eventLoop.run_in_executor( None, functools.partial( _relaySocket.recvfrom, 1024 ) )
	receivedPayload = json.loads( receivedData.decode() )

	if receivedPayload[ "type" ] != Type.Response.value:
		raise Exception( "Received non-response ({0}) data from: {1}".format( receivedPayload[ "type" ], sourcePath ) )

	if receivedPayload[ "status" ] != Status.Success.value:
		raise Exception( "Received non-success ({0}) response from: {1}".format( receivedPayload[ "status" ], sourcePath ) )

	return receivedPayload[ "data" ]

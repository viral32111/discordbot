# Import dependencies
import os, socket, enum, functools, json, asyncio

# Create global variable to hold the path to the socket file
path = None

# Create a TCP unix domain socket
_relayClient = socket.socket( socket.AF_UNIX, socket.SOCK_STREAM )

# Enumerations for status codes
class status( enum.Enum ):
	success = 0
	error = 1

# Enumerations for message types
class type( enum.Enum ):
	response = 0
	status = 1
	message = 2
	command = 3

# Removes the socket file after it has been used
def close():
	if os.path.exists( path ):
		os.remove( path )

# Sets up the unix domain socket
def setup( myPath ):
	# Apply changes to global variables
	global path

	# Update the global path variable
	path = myPath

	# Remove potential lingering socket file from previous use
	close()

	# Bind the unix domain socket and set the default timeout
	_relayClient.bind( path )
	_relayClient.settimeout( 1.0 )

	# Set full permissions on the new socket file
	os.chmod( path, 0o777 )

# Sends a message to another unix domain socket file
async def send( messageType, data, destinationPath ):
	eventLoop = asyncio.get_event_loop()
	await eventLoop.run_in_executor( None, functools.partial( _relayClient.sendto, json.dumps( {
		"type": messageType.value,
		"data": data
	} ).encode( "utf-8" ), destinationPath ) )

	receivedData, sourcePath = await eventLoop.run_in_executor( None, functools.partial( _relayClient.recvfrom, 1024 ) )
	receivedPayload = json.loads( receivedData.decode() )

	if receivedPayload[ "type" ] != Type.Response.value:
		raise Exception( "Received non-response ({0}) data from: {1}".format( receivedPayload[ "type" ], sourcePath ) )

	if receivedPayload[ "status" ] != Status.Success.value:
		raise Exception( "Received non-success ({0}) response from: {1}".format( receivedPayload[ "status" ], sourcePath ) )

	return receivedPayload[ "data" ]

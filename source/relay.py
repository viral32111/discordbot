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
	fetchStatus = 0
	chatMessage = 1
	remoteCommand = 2

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
	#_relayClient.settimeout( 1.0 )

	# Set full permissions on the new socket file
	os.chmod( path, 0o777 )

# Sends a message to another unix domain socket file
def send( messageType, data, destinationPath ):
	_relayClient.connect( destinationPath )

	_relayClient.send( json.dumps( {
		"type": messageType.value,
		"data": data
	} ).encode( "utf-8" ) )

	response = json.loads( _relayClient.recv( 1024 ).decode() )

	_relayClient.close()

	if response[ "status" ] != status.success.value:
		raise Exception( "Received bad response from '{0}': {1}".format( destinationPath, response[ "data" ][ "reason" ] ) )

	return response[ "data" ]

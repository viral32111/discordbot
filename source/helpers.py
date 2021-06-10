import tempfile, mimetypes, functools
import requests

_eventLoop = None

def daySuffix( dayNumber ):
	if 4 <= dayNumber <= 20 or 24 <= dayNumber <= 30:
		return "th"
	else:
		return [ "st", "nd", "rd" ][ dayNumber % 10 - 1 ]

async def httpRequest( *args, **kwargs ):
	if "headers" not in kwargs: kwargs[ "headers" ] = {}
	kwargs[ "headers" ][ "User-Agent" ] = "viral32111's discord bot (https://viral32111.com/contact; contact@viral32111.com)"
	kwargs[ "headers" ][ "From" ] = "contact@viral32111.com"

	return await _eventLoop.run_in_executor( None, functools.partial( requests.request, *args, **kwargs ) )

async def respondToInteraction( interactionData, responseType, responseData ):
	return await httpRequest( "POST", "https://discord.com/api/v9/interactions/{interactionID}/{interactionToken}/callback".format(
		interactionID = interactionData[ "id" ],
		interactionToken = interactionData[ "token" ]
	), headers = {
		"Accept": "application/json",
		"Authorization": "Bot {0}".format( os.environ[ "BOT_TOKEN" ] ),
		"X-Audit-Log-Reason": "Responding to an interaction."
	}, json = {
		"type": responseType,
		"data": responseData
	} )

async def downloadImage( imageURL ):
	response = await httpRequest( "GET", imageURL, headers = {
		"Accept": "image/*"
	}, stream = True )

	fileExtension = mimetypes.guess_extension( response.headers[ "content-type" ] )

	with tempfile.NamedTemporaryFile( dir = "/tmp", prefix = "discordbot-download-", suffix = fileExtension, delete = False ) as imageFile:
		for binaryChunk in response.iter_content( 1024 ):
			imageFile.write( binaryChunk )

		return imageFile.name

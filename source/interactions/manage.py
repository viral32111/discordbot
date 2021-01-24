# Import required modules
import requests, json, dotmap, re

# Globals
CLIENT_ID = "513872128156893189"
GUILD_ID = "240167618575728644"

# Open secrets configuration file
with open( "/data/config/secrets.jsonc", "r" ) as reader:
	secrets = dotmap.DotMap( json.loads( re.sub( r"\/\*[^*]*\*\/| ?\/\/.*", "", reader.read() ) ) )

# Function to make a request to the Discord API
def api( method, endpoint, payload = None ):

	# Execute HTTP request
	response = requests.request(
		method = method,
		url = "https://discord.com/api/v8/{}".format( endpoint ),
		json = payload,
		headers = {
			"Authorization": "Bot {}".format( secrets.token ),
			"User-Agent": "Conspiracy AI (github.com/conspiracy-servers/conspiracy-ai; contact@conspiracyservers.com)",
			"From": "contact@conspiracyservers.com"
		}
	)

	# Print the response
	if len( response.text ) > 0:
		print( response.status_code, json.dumps( response.json(), indent = 4 ) )
	else:
		print( response.status_code )

# Main code
api( "POST", "applications/{}/guilds/{}/commands".format( CLIENT_ID, GUILD_ID ), {
	"name": "ping",
	"description": "A test command to check if the interactions endpoint is operational.",
	"options": [
		{
			"type": 3, # STRING
			"name": "message",
			"description": "Send an optional message along with the command.",
			"required": False
		}
	]
} )

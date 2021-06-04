import os
import requests

applicationID = 839849473266286683

bulkCreateResponse = requests.request( "PUT", "https://discord.com/api/v9/applications/{0}/commands".format( applicationID ), headers = {
	"Accept": "application/json",
	"Authorization": "Bot {0}".format( os.environ[ "BOT_TOKEN" ] ),
	"User-Agent": "viral32111's community discord bot (https://viral32111.com/contact; contact@viral32111.com)",
	"From": "contact@viral32111.com",
	"X-Audit-Log-Reason": "Creating commands for later use."
}, json = [
	{
		"name": "activity",
		"description": "Start an activity in a voice channel.",
		"options": [ {
			"type": 3,
			"name": "type",
			"description": "The type of voice activity to start.",
			"required": True,
			"choices": [
				{ "name": "YouTube Together", "value": "755600276941176913" },
				{ "name": "Poker Night", "value": "755827207812677713" },
				{ "name": "Betrayal.io", "value": "773336526917861400" },
				{ "name": "Fishington.io", "value": "814288819477020702" }
			]
		} ]
	}
] )

print( "{url}\n\n{statusCode} {statusMessage}\n\n{headers}\n\n{body}".format(
	url = bulkCreateResponse.url,
	statusCode = bulkCreateResponse.status_code,
	statusMessage = bulkCreateResponse.reason,
	headers = "\n".join( [ "{0}: {1}".format( name, value ) for name, value in bulkCreateResponse.headers.items() ] ),
	body = bulkCreateResponse.text
) )

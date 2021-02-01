###################################################################################
# Conspiracy AI - The official Discord bot for the Conspiracy Servers community.
# Copyright (C) 2016 - 2021 viral32111 (https://viral32111.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
###################################################################################

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
			"User-Agent": "Conspiracy AI (github.com/conspiracy-servers/conspiracy-ai; contact@viral32111.com)",
			"From": "contact@viral32111.com"
		}
	)

	# Print the response
	if len( response.text ) > 0:
		print( response.status_code, json.dumps( response.json(), indent = 4 ) )
	else:
		print( response.status_code )

# Main code
api( "POST", "applications/{}/guilds/{}/commands".format( CLIENT_ID, GUILD_ID ), {
	"name": "minecraft",
	"description": "Interact with the Minecraft server.",
	"options": [
		{
			"type": 3, # STRING
			"name": "server",
			"description": "Execute power actions on the server.",
			"choices": [
				{
					"name": "start",
					"value": "start"
				},
				{
					"name": "stop",
					"value": "stop"
				},
				{
					"name": "restart",
					"value": "restart"
				}
			]
		},
		{
			"type": 3, # STRING
			"name": "world",
			"description": "Manage the server's world.",
			"choices": [
				{
					"name": "save",
					"value": "save"
				}
			]
		},
		{
			"type": 1, # SUBCOMMAND
			"name": "kick",
			"description": "Kick a player.",
			"options": [
				{
					"type": 3, # STRING
					"name": "name",
					"description": "The name of the player.",
					"required": True
				},
				{
					"type": 3, # STRING
					"name": "reason",
					"description": "The reason for kicking this player.",
					"required": True
				}
			]
		},
		{
			"type": 1, # SUBCOMMAND
			"name": "ban",
			"description": "Ban a player.",
			"options": [
				{
					"type": 3, # STRING
					"name": "name",
					"description": "The name of the player.",
					"required": True
				},
				{
					"type": 3, # STRING
					"name": "reason",
					"description": "The reason for banning this player.",
					"required": True
				},
				{
					"type": 4, # NUMBER
					"name": "duration",
					"description": "How long should this player be banned for"
				}
			]
		}
	]
} )

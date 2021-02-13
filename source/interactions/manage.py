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
	"name": "warn",
	"description": "Issue a warning against a member for breaking a rule.",
	"options": [
		{
			"type": 6, # USER
			"name": "member",
			"description": "The member to warn.",
			"required": True
		},
		{
			"type": 3, # STRING
			"name": "reason",
			"description": "Why are you warning this member?",
			"required": True
		}
	]
} )

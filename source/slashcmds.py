import os
import requests

applicationID = 839849473266286683

bulkCreateResponse = requests.request( "PUT", "https://discord.com/api/v9/applications/{0}/commands".format( applicationID ), headers = {
	"Accept": "application/json",
	"Authorization": "Bot {0}".format( os.environ[ "BOT_TOKEN" ] ),
	"User-Agent": "viral32111's discord bot (https://viral32111.com/contact; contact@viral32111.com)",
	"From": "contact@viral32111.com",
	"X-Audit-Log-Reason": "Creating global application commands."
}, json = [
	{
		"name": "activity",
		"description": "Start an activity in a voice channel.",
		"options": [
			{
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
			}
		]
	},
	{
		"name": "minecraft",
		"description": "Interact with the community Minecraft server.",
		"options": [
			{
				"type": 1,
				"name": "status",
				"description": "Check the current status of the Minecraft server."
			},
			{
				"type": 2,
				"name": "market",
				"description": "Manage offers to buy, sell or trade items in #market.",
				"options": [
					{
						"type": 1,
						"name": "create",
						"description": "Create a new offer in #market.",
						"options": [
							{
								"type": 3,
								"name": "title",
								"description": "A short title for the offer.",
								"required": True
							},
							{
								"type": 3,
								"name": "description",
								"description": "A longer description of your offer, it's best to include information about price or quantity here.",
								"required": True
							},
							{
								"type": 3,
								"name": "image",
								"description": "A direct URL to an image for displaying next to your offer, transparent images work best.",
								"required": False
							}
						]
					},
					{
						"type": 1,
						"name": "modify",
						"description": "Modify an existing offer in #market.",
						"options": [
							{
								"type": 3,
								"name": "message",
								"description": "The ID of the message in #market that contains the offer.",
								"required": True
							},
							{
								"type": 3,
								"name": "title",
								"description": "A short title for the offer.",
								"required": True
							},
							{
								"type": 3,
								"name": "description",
								"description": "A longer description of your offer, it's best to include information about price or quantity here.",
								"required": True
							},
							{
								"type": 3,
								"name": "image",
								"description": "A direct URL to an image for displaying next to your offer, transparent images work best.",
								"required": False
							}
						]
					},
					{
						"type": 1,
						"name": "remove",
						"description": "Remove an existing offer in #market.",
						"options": [
							{
								"type": 3,
								"name": "message",
								"description": "The ID of the message in #market that contains the offer.",
								"required": True
							}
						]
					}
				]
			}
		]
	},
	{
		"name": "anonymous",
		"description": "Interact with the #anonymous channel.",
		"options": [
			{
				"type": 1,
				"name": "say",
				"description": "Quickly send a message to #anonymous. Direct message me for more functionality.",
				"options": [
					{
						"type": 3,
						"name": "message",
						"description": "The message to send. Markdown is supported.",
						"required": True
					}
				]
			},
			{
				"type": 1,
				"name": "delete",
				"description": "Delete a message you sent in #anonymous. Sender authenticity is checked using one-way hashes.",
				"options": [
					{
						"type": 3,
						"name": "id",
						"description": "The ID of the message to delete.",
						"required": True
					}
				]
			}
		]
	}
] )

print( "{url}\n\n{statusCode} {statusMessage}\n\n{headers}\n\n{body}".format(
	url = bulkCreateResponse.url,
	statusCode = bulkCreateResponse.status_code,
	statusMessage = bulkCreateResponse.reason,
	headers = "\n".join( [ "{0}: {1}".format( name, value ) for name, value in bulkCreateResponse.headers.items() ] ),
	body = bulkCreateResponse.text
) )

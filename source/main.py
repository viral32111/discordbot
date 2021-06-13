# TO-DO: Discord to Minecraft relay - Datagram unix sockets, steal bridge code
# TO-DO: #anonymous relay - Client-only slash commands?
# TO-DO: #market channel buy/sell listings for the Minecraft server
# TO-DO: Logging for every gateway event.
# TO-DO: Basic music bot to replace Groovy.
# TO-DO: /minecraft slash command to fetch Minecraft server info & status.
# TO-DO: Store member information and statistics in SQLite database.
# TO-DO: Repost detection.

# Import dependencies
import os, functools, socket, json, re, datetime, tempfile, mimetypes
import discord, requests, emoji, colorthief
import relay, helpers

# Set global constant variables
PRIMARY_SERVER_ID = 240167618575728644
MARKET_CHANNEL_ID = 852114085750636584
STAGE_CHANNEL_ID = 826908363392680026
LURKER_ROLE_ID = 807559722127458304

# Define global variables
primaryServer = None
bot = discord.Client(
	intents = discord.Intents.all(), # Receive all events
	allowed_mentions = discord.AllowedMentions.none() # Prevent mentioning anyone
)

# Setup imported code
relay.setup( "discordbot" )

# Log events to console
def log( message ):
	# Rules of logging:
	# * User controlled values should be wrapped in single quotes
	# * Additional information comes after primary information in brackets
	# * Applicable values should be prefixed or suffixed to indicate what they mean
	# * Lists should be wrapped in square brackets
	# * Anything that is void should be replaced with a placeholder hyphen
	# * Do not relog past information, just give an ID to refer back to it
	# * Respect user privacy and redact information for direct messages

	print( "[{datetime:%d-%m-%Y %H:%M:%S.%f} +0000] {message}".format(
		datetime = datetime.datetime.utcnow(),
		message = message,
	) )

# Runs when the session is opened
async def on_connect():
	# Log a message to the console
	log( "Connected!" )

# Runs when the session is closed
async def on_disconnect():
	# Log a message to the console
	log( "Disconnected." )

# Runs when the session is reopened
async def on_resume():
	# Log a message to the console
	log( "Resumed!" )

# Runs when a message is received...
async def on_message( message ):
	# Ignore message pinned and member joined messages since we have events for those
	if message.type == discord.MessageType.pins_add or message.type == discord.MessageType.new_member: return

	# Log this event to the console
	log( "{memberName} ({memberNick}, {memberTag}, {memberID}) sent {messageType} message {messageContent} [{attachments}] [{stickers}] [{embeds}] {application} ({messageLength}, {messageID}) {messageReference}in {location}".format(
		memberName = ( "'{0}'".format( emoji.demojize( message.author.name ) ) if message.guild else "#REDACTED#" ),
		memberNick = ( "'{0}'".format( emoji.demojize( message.author.nick ) ) if not message.author.bot and message.guild and message.author.nick else "-" ),
		memberTag = ( "-" if message.webhook_id else ( "#{0}".format( message.author.discriminator ) if message.guild else "#REDACTED#" ) ),
		memberID = ( message.author.id if message.guild else "#REDACTED#" ),

		messageType = ( "system" if message.is_system() and not message.type == discord.MessageType.reply else ( "spoken" if message.tts else "regular" ) ),

		messageContent = ( emoji.demojize( message.system_content ) if message.is_system() else ( ", ".join( [ ( "'{0}'".format( emoji.demojize( line ) ) if line != "" else "-" ) for line in message.content.split( "\n" ) ] ) if message.content else "-" ) ),
		attachments = (
			( ", ".join( [ "'{attachmentName}' ({attachmentType}, {attachmentSize}B, {attachmentWidth}, {attachmentHeight}, {attachmentID})".format(
				attachmentName = attachment.filename,
				attachmentType = ( attachment.content_type or "-" ),
				attachmentSize = attachment.size,
				attachmentWidth = ( "{0}px".format( attachment.width ) if attachment.width else "-" ),
				attachmentHeight = ( "{0}px".format( attachment.height ) if attachment.height else "-" ),
				attachmentID = attachment.id
			) for attachment in message.attachments ] ) ) if len( message.attachments ) > 0 else ""
		),
		stickers = (
			( ", ".join( [ "'{stickerName}' ({stickerType}, {packID}, {stickerID})".format(
				stickerName = sticker.name,
				stickerType = sticker.format,
				packID = sticker.pack_id,
				stickerID = sticker.id
			) for sticker in message.stickers ] ) ) if len( message.stickers ) > 0 else ""
		),
		embeds = ( ", ".join( [ str( embed.to_dict() ) for embed in message.embeds ] ) if len( message.embeds ) > 0 else "" ),
		application = ( str( message.application ) if message.application else "-" ),
		messageLength = len( message.content ),
		messageID = ( message.id if message.guild else "#REDACTED#" ),

		messageReference = ( "referencing {messageID} ({channelID}, {serverID}) ".format(
			messageID = ( message.reference.message_id if message.guild else "#REDACTED#" ),
			channelID = ( message.reference.channel_id if message.guild else "#REDACTED#" ),
			serverID = ( message.reference.guild_id or "-" )
		) if message.reference else "" ),

		location = (
			( "'{serverName}' ({serverID}) -> '{categoryName}' ({categoryID}) -> '#{channelName}' ({channelID})".format(
				serverName = emoji.demojize( message.guild.name ),
				serverID = message.guild.id,
				
				categoryName = emoji.demojize( message.channel.category.name ),
				categoryID = message.channel.category.id,

				channelName = emoji.demojize( message.channel.name ),
				channelID = message.channel.id
			) if message.channel.category else "'{serverName}' ({serverID}) -> '#{channelName}' ({channelID})".format(
				serverName = emoji.demojize( message.guild.name ),
				serverID = message.guild.id,
				
				channelName = emoji.demojize( message.channel.name ),
				channelID = message.channel.id
			) ) if message.guild else "direct messages ({channelID}).".format(
				channelID = ( message.channel.id if message.guild else "#REDACTED#" ) # This check is pointless
			)
		)
	) )

	if message.channel.id == 851437359237169183 and not message.author.bot and len( message.content ) > 0:
		try:
			await relay.send( relay.type.message, {
				"username": emoji.demojize( message.author.display_name ),
				"content": emoji.demojize( message.clean_content.replace( "\n", " " ) ),
				"color": message.author.color.value
			}, "minecraft" )
		except Exception as exception:
			await message.reply( ":interrobang: Your message could not be sent due to an internal error!" )
			raise exception

async def on_member_join( member ):
	# TO-DO: h0nde has been banned from twitter, so remove this if no bots join for a few weeks?
	if re.search( r"twitter\.com\/h0nde", member.name, flags = re.IGNORECASE ):
		await member.add_roles( primaryServer.get_role( LURKER_ROLE_ID ), reason = "Dumb spam bot >:(" )
		await primaryServer.system_channel.send( ":anger: {memberMention} is a dumb spam bot.".format(
			memberMention = member.mention
		) )
	else:
		await primaryServer.system_channel.send( ":wave_tone1: {memberMention} joined the community!".format(
			memberMention = member.mention
		) )

async def on_member_remove( member ):
	await primaryServer.system_channel.send( "{memberName}#{memberTag} left the community.".format(
		memberName = member.name,
		memberTag = member.discriminator
	) )

async def on_guild_update( oldServer, newServer ):
	serverTemplate = ( await newServer.templates() )[ 0 ]
	await serverTemplate.sync()
	log( "Synced template '{templateName}' ({templateCode}) due to server update event.".format(
		templateName = serverTemplate.name,
		templateCode = serverTemplate.code
	) )

async def on_guild_channel_create( channel ):
	serverTemplate = ( await channel.guild.templates() )[ 0 ]
	await serverTemplate.sync()
	log( "Synced template '{templateName}' ({templateCode}) due to channel create event.".format(
		templateName = serverTemplate.name,
		templateCode = serverTemplate.code
	) )

async def on_guild_channel_delete( channel ):
	serverTemplate = ( await channel.guild.templates() )[ 0 ]
	await serverTemplate.sync()
	log( "Synced template '{templateName}' ({templateCode}) due to channel delete event.".format(
		templateName = serverTemplate.name,
		templateCode = serverTemplate.code
	) )

async def on_guild_channel_update( oldChannel, newChannel ):
	if newChannel.id == STAGE_CHANNEL_ID and newChannel.name != "Stage":
		await newChannel.edit(
			name = "Stage",
			reason = "Do not rename this channel! >:("
		)

	serverTemplate = ( await newChannel.guild.templates() )[ 0 ]
	await serverTemplate.sync()
	log( "Synced template '{templateName}' ({templateCode}) due to channel update event.".format(
		templateName = serverTemplate.name,
		templateCode = serverTemplate.code
	) )

async def on_guild_role_create( role ):
	serverTemplate = ( await role.guild.templates() )[ 0 ]
	await serverTemplate.sync()
	log( "Synced template '{templateName}' ({templateCode}) due to role create event.".format(
		templateName = serverTemplate.name,
		templateCode = serverTemplate.code
	) )

async def on_guild_role_delete( role ):
	serverTemplate = ( await role.guild.templates() )[ 0 ]
	await serverTemplate.sync()
	log( "Synced template '{templateName}' ({templateCode}) due to role delete event.".format(
		templateName = serverTemplate.name,
		templateCode = serverTemplate.code
	) )

async def on_guild_role_update( oldRole, newRole ):
	serverTemplate = ( await newRole.guild.templates() )[ 0 ]
	await serverTemplate.sync()
	log( "Synced template '{templateName}' ({templateCode}) due to role update event.".format(
		templateName = serverTemplate.name,
		templateCode = serverTemplate.code
	) )

async def on_application_command( data ):
	if "guild_id" not in data:
		log( "{userName}#{userTag} attempted to use my commands in Direct Messages".format(
			userName = data[ "user" ][ "username" ],
			userTag = data[ "user" ][ "discriminator" ],
		) )

		return await helpers.respondToInteraction( data, 4, {
			"content": "Sorry, I do not work in Direct Messages yet! Please stick to using my commands in the server for now.",
			"flags": 64
		} )

	server = bot.get_guild( int( data[ "guild_id" ] ) )
	channel = server.get_channel( int( data[ "channel_id" ] ) )
	member = server.get_member( int( data[ "member" ][ "user" ][ "id" ] ) )

	if data[ "data" ][ "name" ] == "activity":
		if not member.voice:
			log( "{memberName}#{memberTag} attempted to start a voice activity without being in a voice channel".format(
				memberName = member.name,
				memberTag = member.discriminator
			) )

			return await helpers.respondToInteraction( data, 4, {
				"content": "You first need to join a voice channel to start an activity!",
				"flags": 64
			} )

		if member.voice.channel.type != discord.ChannelType.voice:
			log( "{memberName}#{memberTag} attempted to start a voice activity without being in a regular voice channel".format(
				memberName = member.name,
				memberTag = member.discriminator
			) )

			return await helpers.respondToInteraction( data, 4, {
				"content": "Only regular voice channels are supported!",
				"flags": 64
			} )

		inviteResponse = await helpers.httpRequest( "POST", "https://discord.com/api/v9/channels/{channelID}/invites".format(
			channelID = member.voice.channel.id
		), headers = {
			"Accept": "application/json",
			"Authorization": "Bot {0}".format( os.environ[ "BOT_TOKEN" ] ),
			"X-Audit-Log-Reason": "Starting activity in a voice channel."
		}, json = {
			"max_age": 3600,
			"target_type": 2,
			"target_application_id": data[ "data" ][ "options" ][ 0 ][ "value" ]
		} )

		await helpers.respondToInteraction( data, 4, {
			"content": "[Click me to start!](<https://discord.gg/{inviteCode}>) This link will expire in 1 hour.".format( inviteCode = inviteResponse.json()[ "code" ] ),
			"allowed_mentions": { "parse": [] }
		} )

		log( "{memberName}#{memberTag} started voice activity {activityID} in voice channel {channelID}: discord.gg/{inviteCode}".format(
			memberName = member.name,
			memberTag = member.discriminator,
			activityID = data[ "data" ][ "options" ][ 0 ][ "value" ],
			channelID = member.voice.channel.id,
			inviteCode = inviteResponse.json()[ "code" ]
		) )

	elif data[ "data" ][ "name" ] == "minecraft":
		if data[ "data" ][ "options" ][ 0 ][ "name" ] == "status":
			await helpers.respondToInteraction( data, 4, {
				"content": ":no_entry_sign: no, not yet :no_entry_sign:",
				"flags": 64
			} )

		elif data[ "data" ][ "options" ][ 0 ][ "name" ] == "market":
			options = { option[ "name" ]: option[ "value" ] for option in data[ "data" ][ "options" ][ 0 ][ "options" ][ 0 ][ "options" ] }

			if data[ "data" ][ "options" ][ 0 ][ "options" ][ 0 ][ "name" ] == "create":
				# TO-DO: Input validation!
				# if title longer than 50 chars
				# if title is invisible characters/empty markdown
				# if description longer than 500 chars
				# if description is invisible characters/empty markdown
				# if image is not a valid url / does not point to a valid image
				# if message id is not valid / does not point to an existing offer

				await helpers.respondToInteraction( data, 5, {
					"content": "",
					"flags": 64
				} )

				color = 0xD8804D

				if "image" in options:
					thumbnailDownloadPath = await helpers.downloadImage( options[ "image" ] )
					dominantColorRed, dominantColorGreen, dominantColorBlue = colorthief.ColorThief( thumbnailDownloadPath ).get_color( quality = 3 )
					color = ( dominantColorRed * 65536 ) + ( dominantColorGreen * 256 ) + dominantColorBlue

				rightNowUTC = datetime.datetime.utcnow()

				offerMessagePayload = {
					"embed": {
						"title": options[ "title" ],
						"description": options[ "description" ],
						"color": color,
						"author": {
							"name": "{memberName}#{memberTag}".format(
								memberName = member.name,
								memberTag = member.discriminator
							),
							"icon_url": "https://cdn.discordapp.com/avatars/{memberID}/{memberAvatar}.png".format(
								memberID = member.id,
								memberAvatar = member._user._avatar
							)
						},
						"footer": {
							"text": "Offer posted on {rightNow:%A} {rightNow:%-d}{daySuffix} {rightNow:%B} {rightNow:%Y} at {rightNow:%-H}:{rightNow:%M} UTC.".format(
								rightNow = rightNowUTC,
								daySuffix = helpers.daySuffix( rightNowUTC.day )
							),
							"icon_url": "https://i.imgur.com/WyrN3ml.png"
						}
					},
					"components": [
						{
							"type": 1,
							"components": [
								{
									"type": 2,
									"style": 5,
									"label": "Discord Profile",
									"url": "https://discord.com/users/{memberID}".format(
										memberID = member.id
									),
									"disabled": False
								},
								{
									"type": 2,
									"style": 4,
									"label": "Remove",
									"custom_id": "remove-{memberID}".format(
										memberID = member.id
									),
									"disabled": False
								}
							]
						}
					]
				}

				if "image" in options:
					offerMessagePayload[ "embed" ][ "thumbnail" ] = {
						"url": options[ "image" ]
					}

				offerMessageResponse = await helpers.httpRequest( "POST", "https://discord.com/api/v9/channels/{channelID}/messages".format(
					channelID = MARKET_CHANNEL_ID
				), headers = {
					"Accept": "application/json",
					"Authorization": "Bot {0}".format( os.environ[ "BOT_TOKEN" ] ),
					"X-Audit-Log-Reason": "Creating an offer in #market."
				}, json = offerMessagePayload )

				offerMessage = offerMessageResponse.json()

				return await helpers.httpRequest( "PATCH", "https://discord.com/api/v9/webhooks/{applicationID}/{interactionToken}/messages/@original".format(
					applicationID = data[ "application_id" ],
					interactionToken = data[ "token" ]
				), headers = {
					"Accept": "application/json",
					"Authorization": "Bot {0}".format( os.environ[ "BOT_TOKEN" ] ),
					"X-Audit-Log-Reason": "Updating an interaction response."
				}, json = {
					"content": "Done! Your offer has been created in <#{channelID}>.\n\nThe offer's message ID is `{messageID}`, you will need this in the future if you wish to modify it using `/minecraft market modify`. Don't worry if you forget it or lose this response, you can always get it again by right clicking on the offer's message and clicking *Copy ID*.\n\nDirect link to the offer: <{messageLink}>.".format(
						channelID = MARKET_CHANNEL_ID,
						messageID = offerMessage[ "id" ],
						messageLink = "https://discord.com/channels/{serverID}/{channelID}/{messageID}".format(
							serverID = server.id,
							channelID = MARKET_CHANNEL_ID,
							messageID = offerMessage[ "id" ],
						)
					),
					"flags": 64
				} )

			elif data[ "data" ][ "options" ][ 0 ][ "options" ][ 0 ][ "name" ] == "modify":
				# TO-DO: The date and time the offer was modified in UTC [FOOTER]

				return await helpers.respondToInteraction( data, 4, {
					"content": ":no_entry_sign: no, not yet :no_entry_sign:",
					"flags": 64
				} )

			elif data[ "data" ][ "options" ][ 0 ][ "options" ][ 0 ][ "name" ] == "remove":
				return await helpers.respondToInteraction( data, 4, {
					"content": ":no_entry_sign: no, not yet :no_entry_sign:",
					"flags": 64
				} )

async def on_message_component( data ):
	callingMemberID = int( data[ "member" ][ "user" ][ "id" ] )
	customName, customData = data[ "data" ][ "custom_id" ].split( "-" )

	await helpers.respondToInteraction( data, 6, None )

	if customName == "remove":
		if callingMemberID == int( customData ):
			# TO-DO: Removal confirmation by updating the button text

			await helpers.httpRequest( "DELETE", "https://discord.com/api/v9/channels/{channelID}/messages/{messageID}".format(
				channelID = data[ "channel_id" ],
				messageID = data[ "message" ][ "id" ]
			), headers = {
				"Authorization": "Bot {0}".format( os.environ[ "BOT_TOKEN" ] ),
				"X-Audit-Log-Reason": "Removing a #market offer message."
			} )

async def on_socket_response( payload ):
	if payload[ "t" ] == "INTERACTION_CREATE":
		if payload[ "d" ][ "type" ] == 2:
			bot.dispatch( "application_command", payload[ "d" ] )
		elif payload[ "d" ][ "type" ] == 3:
			bot.dispatch( "message_component", payload[ "d" ] )

# Runs when the bot is ready...
async def on_ready():
	# Apply changes to global variables
	global primaryServer

	# Register post-ready event handlers
	bot.event( on_message )
	bot.event( on_member_join )
	bot.event( on_member_remove )
	bot.event( on_guild_update )
	bot.event( on_guild_channel_create )
	bot.event( on_guild_channel_delete )
	bot.event( on_guild_channel_update )
	bot.event( on_guild_role_create )
	bot.event( on_guild_role_delete )
	bot.event( on_guild_role_update )
	bot.event( on_application_command )
	bot.event( on_message_component )
	bot.event( on_socket_response )
	log( "Registered post-ready event handlers." )

	# Log a message to the console
	log( "Logged in as '{botName}' (#{botTag}, {botID}) on {serverCount} server(s): {serverList}".format(
		botName = bot.user.name,
		botTag = bot.user.discriminator,
		botID = bot.user.id,
		serverCount = len( bot.guilds ),
		serverList = ( ", ".join( [ "'{serverName}' ({serverID})".format(
			serverName = emoji.demojize( server.name ),
			serverID = server.id
		) for server in bot.guilds ] ) )
	) )

	# Store the primary server instance for later use
	primaryServer = bot.get_guild( PRIMARY_SERVER_ID )
	log( "The primary server is '{serverName}' ({serverID})".format(
		serverName = emoji.demojize( primaryServer.name ),
		serverID = primaryServer.id
	) )

	# Disable default join notifications on the server
	systemChannelFlags = primaryServer.system_channel_flags
	systemChannelFlags.join_notifications = False
	await primaryServer.edit(
		system_channel_flags = systemChannelFlags,
		reason = "Disable default join messages in favour of custom join messages."
	)
	log( "Disabled default join messages for '{serverName}' ({serverID})".format(
		serverName = emoji.demojize( primaryServer.name ),
		serverID = primaryServer.id
	) )

	# Set the bot's current activity
	await bot.change_presence(
		activity = discord.Activity(
			name = "all of you.",
			type = discord.ActivityType.watching
		)
	)
	log( "Updated current activity." )

	# Log a message to the console
	log( "Ready!" )

# Register pre-ready event handlers
bot.event( on_connect )
bot.event( on_disconnect )
bot.event( on_resume )
bot.event( on_ready )
log( "Registered pre-ready event handlers." )

try:
	log( "Connecting..." )
	bot.loop.run_until_complete( bot.start( os.environ[ "BOT_TOKEN" ] ) )
except KeyboardInterrupt:
	log( "Stopping..." )

	# Remove all event handlers
	del bot.on_connect
	del bot.on_disconnect
	del bot.on_resume
	del bot.on_ready
	del bot.on_message
	del bot.on_member_join
	del bot.on_member_remove
	del bot.on_guild_update
	del bot.on_guild_channel_create
	del bot.on_guild_channel_delete
	del bot.on_guild_channel_update
	del bot.on_guild_role_create
	del bot.on_guild_role_delete
	del bot.on_guild_role_update
	del bot.on_application_command
	del bot.on_message_component
	del bot.on_socket_response
	log( "Removed all event handlers." )

	# Gracefully close and cleanup the relay
	relay.cleanup()
	log( "Closed and cleaned up relay." )

	# Enable default join notifications on the server
	primaryServer = bot.get_guild( PRIMARY_SERVER_ID ) # Fetch again in-case we never got to the ready event
	systemChannelFlags = primaryServer.system_channel_flags
	systemChannelFlags.join_notifications = True
	bot.loop.run_until_complete( primaryServer.edit(
		system_channel_flags = systemChannelFlags,
		reason = "Enable default join messages."
	) )
	log( "Enabled default join messages for '{serverName}' ({serverID})".format(
		serverName = emoji.demojize( primaryServer.name ),
		serverID = primaryServer.id
	) )

	bot.loop.run_until_complete( bot.change_presence( status = discord.Status.offline ) )
	log( "Cleared activity and set status to offline." )

	bot.loop.run_until_complete( bot.close() )
finally:
	bot.loop.close()

# TO-DO: Discord to Minecraft relay - Datagram unix sockets, steal bridge code
# TO-DO: #anonymous relay - Client-only slash commands?
# TO-DO: #market channel buy/sell listings for the Minecraft server
# TO-DO: Logging for every gateway event.
# TO-DO: Basic music bot to replace Groovy.
# TO-DO: /minecraft slash command to fetch Minecraft server info & status.
# TO-DO: Store member information and statistics in SQLite database.
# TO-DO: Repost detection.
# TO-DO: Move external images into repository.

# Import dependencies
import os, re, datetime, sqlite3, hashlib, random
import discord, emoji, colorthief
import helpers, logs, history # relay

# Set global constant configuration variables
LOG_PATH_TEMPLATE = "logs/{0}.log"
SOCKET_PATH_TEMPLATE = "/var/run/relay/{0}.sock"
PRIMARY_SERVER_ID = 240167618575728644
MARKET_CHANNEL_ID = 852114085750636584
#RELAY_CHANNEL_ID = 856631516762079253
STAGE_CHANNEL_ID = 826908363392680026
HISTORY_CHANNEL_ID = 576904701304635405
ANONYMOUS_CHANNEL_ID = 661694045600612352
LURKER_ROLE_ID = 807559722127458304
MUTED_ROLE_ID = 539160858341933056
YEAR_2021_ROLE_ID = 804869340225863691
YEAR_2022_ROLE_ID = 929497402149322752

# Define global variables
primaryServer = None
anonymousCooldowns = {}
bot = discord.Client(
	max_messages = 1000000, # Cache way more messages 
	intents = discord.Intents.all(), # Receive all events
	allowed_mentions = discord.AllowedMentions.none() # Prevent mentioning anyone
)

# Start logging
logs.start( LOG_PATH_TEMPLATE )

# Setup the relay
#relay.setup( SOCKET_PATH_TEMPLATE.format( "discordbot" ) )
#logs.write( "Setup the relay socket in '{socketPath}'.".format(
#	socketPath = relay.path
#) )

# Setup the local database
anonymousDatabaseConnection = sqlite3.connect( "data/anonymous.db" )
anonymousDatabaseCursor = anonymousDatabaseConnection.cursor()
anonymousDatabaseCursor.execute( "CREATE TABLE IF NOT EXISTS Messages ( Identifier INTEGER, Sender TEXT )" )
anonymousDatabaseConnection.commit()

# Runs when the session is opened
async def on_connect():
	# Log a message to the console
	logs.write( "Connected!" )

# Runs when the session is closed
async def on_disconnect():
	# Log a message to the console
	logs.write( "Disconnected." )

# Runs when the session is reopened
async def on_resumed():
	# Log a message to the console
	logs.write( "Resumed!" )

# Runs when a message is received...
async def on_message( message ):
	# Apply changes to global variables
	global anonymousCooldowns

	# Ignore message pinned and member joined messages since we have events for those
	if message.type == discord.MessageType.pins_add or message.type == discord.MessageType.new_member: return

	# Log this event to the console
	logs.write( "{authorName} ({authorNick}, {authorTag}, {authorID}) sent {messageType} message {messageContent} [{attachments}] [{stickers}] [{embeds}] {application} ({messageLength}, {messageID}) {messageReference}in {location}.".format(
		authorName = ( "'{0}'".format( emoji.demojize( message.author.name ) ) if message.guild else "-HIDDEN-" ),
		authorNick = ( "'{0}'".format( emoji.demojize( message.author.nick ) ) if not message.author.bot and message.guild and message.author.nick else "-" ),
		authorTag = ( "-" if message.webhook_id else ( "#{0}".format( message.author.discriminator ) if message.guild else "-HIDDEN-" ) ),
		authorID = ( message.author.id if message.guild else "-HIDDEN-" ),

		messageType = ( "system" if message.is_system() and not message.type == discord.MessageType.reply else ( "spoken" if message.tts else "regular" ) ),

		messageContent = ( "'{0}'".format( emoji.demojize( message.system_content ) ) if message.is_system() and not message.type == discord.MessageType.reply and not message.type == discord.MessageType.application_command else ( ", ".join( [ ( "'{0}'".format( emoji.demojize( line ) ) if line != "" else "-" ) for line in message.content.split( "\n" ) ] ) if message.content else "-" ) ),

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
		messageID = ( message.id if message.guild else "-HIDDEN-" ),

		messageReference = ( "referencing {{{messageID}}} ({channelID}, {serverID}) ".format(
			messageID = ( message.reference.message_id if message.guild else "-HIDDEN-" ),
			channelID = ( message.reference.channel_id if message.guild else "-HIDDEN-" ),
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
			) ) if message.guild else "direct messages"
		)
	) )

	# Ignore bot messages
	if message.author.bot: return

	# Is this the Minecraft relay channel?
	#if message.channel.id == RELAY_CHANNEL_ID and len( message.content ) != 0:

		# Attempt to relay the message to the Minecraft server
		#try:
		#	relay.send( relay.type.chatMessage, {
		#		"username": emoji.demojize( message.author.display_name ),
		#		"content": emoji.demojize( message.clean_content.replace( "\n", " " ) ),
		#		"color": message.author.color.value
		#	}, SOCKET_PATH_TEMPLATE.format( "minecraft" ) )

		# Notify the user of an error if one happens
		#except Exception as exception:
		#	await message.reply( ":interrobang: Your message could not be sent due to an internal error!" )
		#	raise exception

	# Is this in Direct Messages?
	if not message.guild:
		server = bot.get_guild( PRIMARY_SERVER_ID )
		member = server.get_member( message.author.id )
		anonymousChannel = server.get_channel( ANONYMOUS_CHANNEL_ID )
		lurkerRole = server.get_role( LURKER_ROLE_ID )
		mutedRole = server.get_role( MUTED_ROLE_ID )
		rightNow = datetime.datetime.now( datetime.timezone.utc ).timestamp()

		if not member:
			return await message.reply( ":interrobang: The <#{0}> channel can only be used by members in the server!".format( anonymousChannel.id ) )

		if lurkerRole in member.roles:
			return await message.reply( ":interrobang: The <#{0}> channel cannot be used by lurkers!".format( anonymousChannel.id ) )

		if mutedRole in member.roles:
			return await message.reply( ":interrobang: The <#{0}> channel cannot be used by muted members!.".format( anonymousChannel.id ) )

		if str( member.id ) in anonymousCooldowns and rightNow < anonymousCooldowns[ str( member.id ) ]:
			return await message.reply( ":interrobang: Wait a few seconds before sending another <#{0}> message.".format( anonymousChannel.id ) )

		if len( message.embeds ) > 0:
			return await message.reply( ":interrobang: Embeds cannot be forwarded to the <#{0}> channel.".format( anonymousChannel.id ) )

		anonymousCooldowns[ str( member.id ) ] = rightNow + 3
		totalMessageCount = anonymousDatabaseCursor.execute( "SELECT COUNT( Identifier ) FROM Messages" ).fetchone()[ 0 ]
		anonymousWebhook = ( await anonymousChannel.webhooks() )[ 0 ]

		# the code exists for multiple messages below but it just doesn't work that well, sometimes it misses attachments
		if len( message.attachments ) > 1:
			return await message.reply( ":interrobang: Messages with more than 1 attachment cannot be forwarded to the <#{0}> channel.".format( anonymousChannel.id ) )

		filesToUpload = []
		for attachment in message.attachments:
			downloadedPath = await helpers.downloadFile( attachment.url )
			_, fileExtension = os.path.splitext( downloadedPath )
			filesToUpload.append( discord.File( downloadedPath, filename = "unknown{0}".format( fileExtension ), spoiler = attachment.is_spoiler() ) )

		try:
			newMessage = await anonymousWebhook.send(
				content = message.content,
				files = filesToUpload,
				username = "#{0:,}".format( totalMessageCount + 1 ),
				avatar_url = "https://discord.com/embed/avatars/{0}.png".format( random.randint( 0, 5 ) ),
				wait = True
			)

			hashedSender = hashlib.sha512( "{0}{1}{2}".format( os.environ[ "ANONYMOUS_SALT" ], member.id, newMessage.id ).encode() ).hexdigest()
			anonymousDatabaseCursor.execute( "INSERT INTO Messages VALUES ( ?, ? )", ( newMessage.id, hashedSender ) )
			anonymousDatabaseConnection.commit()
		except discord.errors.HTTPException as exception:
			if exception.code == 40005:
				await message.reply( "Unable to forward message because it is too large.\nIf you uploaded multiple files in a single message, try uploading them in seperate messages." )

# Runs when a message is deleted...
async def on_raw_message_delete( rawMessage ):
	# TO-DO: Make it work for non-cached messages!
	if not rawMessage.cached_message: return

	# Fetch the member/user that deleted this message
	if rawMessage.guild_id:
		server = bot.get_guild( rawMessage.cached_message.guild.id )
		deleterID = await history.fetchMessageDeleter( rawMessage.cached_message.guild.id, rawMessage.cached_message.channel.id, rawMessage.cached_message.author.id )
		deleter = ( server.get_member( deleterID ) if deleterID else None )
	else:
		deleter = rawMessage.cached_message.author

	# Log this event to the console
	logs.write( "{deleterName} ({deleterNick}, {deleterTag}, {deleterID}) deleted {messageType} message {{{messageID}}} sent by {authorName} ({authorNick}, {authorTag}, {authorID}) in {location}.".format(
		deleterName = ( ( "'{0}'".format( emoji.demojize( deleter.name ) ) if deleter else "-" ) if rawMessage.cached_message.guild else "-HIDDEN-" ),
		deleterNick = ( "'{0}'".format( emoji.demojize( deleter.nick ) ) if rawMessage.guild_id and deleter and deleter.nick else "-" ),
		deleterTag = ( ( "#{0}".format( deleter.discriminator ) if deleter else "-" ) if rawMessage.cached_message.guild else "-HIDDEN-" ),
		deleterID = ( ( deleter.id if deleter else "-" ) if rawMessage.cached_message.guild else "-HIDDEN-" ),

		messageType = ( "system" if rawMessage.cached_message.is_system() and not rawMessage.cached_message.type == discord.MessageType.reply else ( "spoken" if rawMessage.cached_message.tts else "regular" ) ),
		messageID = rawMessage.cached_message.id,

		authorName = ( "'{0}'".format( emoji.demojize( rawMessage.cached_message.author.name ) ) if rawMessage.cached_message.guild else "-HIDDEN-" ),
		authorNick = ( "'{0}'".format( emoji.demojize( rawMessage.cached_message.author.nick ) ) if not rawMessage.cached_message.author.bot and rawMessage.cached_message.guild and rawMessage.cached_message.author.nick else "-" ),
		authorTag = ( "-" if rawMessage.cached_message.webhook_id else ( "#{0}".format( rawMessage.cached_message.author.discriminator ) if rawMessage.cached_message.guild else "-HIDDEN-" ) ),
		authorID = ( rawMessage.cached_message.author.id if rawMessage.cached_message.guild else "-HIDDEN-" ),

		location = (
			( "'{serverName}' ({serverID}) -> '{categoryName}' ({categoryID}) -> '#{channelName}' ({channelID})".format(
				serverName = emoji.demojize( rawMessage.cached_message.guild.name ),
				serverID = rawMessage.cached_message.guild.id,
				
				categoryName = emoji.demojize( rawMessage.cached_message.channel.category.name ),
				categoryID = rawMessage.cached_message.channel.category.id,

				channelName = emoji.demojize( rawMessage.cached_message.channel.name ),
				channelID = rawMessage.cached_message.channel.id
			) if rawMessage.cached_message.channel.category else "'{serverName}' ({serverID}) -> '#{channelName}' ({channelID})".format(
				serverName = emoji.demojize( rawMessage.cached_message.guild.name ),
				serverID = rawMessage.cached_message.guild.id,
				
				channelName = emoji.demojize( rawMessage.cached_message.channel.name ),
				channelID = rawMessage.cached_message.channel.id
			) ) if rawMessage.cached_message.guild else "direct messages"
		)
	) )

	# Ignore Direct Messages
	if not rawMessage.cached_message.guild: return

	# Ignore bots and webhooks
	if rawMessage.cached_message.author.bot or rawMessage.cached_message.webhook_id: return

	# Ignore the history channel
	if rawMessage.cached_message.channel.id == HISTORY_CHANNEL_ID: return

	# Ignore private channels
	if rawMessage.cached_message.channel.overwrites_for( rawMessage.cached_message.guild.default_role ).pair()[ 1 ].view_channel == True: return

	# Create a list for the embed fields
	logFields = [
		[ "Author", rawMessage.cached_message.author.mention, True ],
		[ "Deleter", ( deleter.mention if deleter else "Unknown" ), True ],
		[ "Channel", rawMessage.cached_message.channel.mention, True ]
	]

	# Add the embed field for the message, if applicable
	if len( rawMessage.cached_message.clean_content ) > 0:
		logFields.append( [ "Message", history.cleanMessage( rawMessage.cached_message ), False ] )
	elif len( rawMessage.cached_message.embeds ) > 0:
		logFields.append( [ "Message", "Content not displayable.", False ] )

	# Add the embed field for the attachments, if applicable
	if len( rawMessage.cached_message.attachments ) > 0:
		logFields.append( [ "Attachments", history.formatAttachments( rawMessage.cached_message.attachments ), False ] )

	# Log this event in the logging channel
	await history.send( rawMessage.cached_message.guild, HISTORY_CHANNEL_ID, "Message Deleted", logFields )

	# For uncached messages:
	#deletedByID, sentByID = await history.fetchMessageDeleter( rawMessage.guild_id, rawMessage.channel_id, None )
	#if sentByID:
	#	sentBy = bot.get_user( sentByID )
	#	logContents.append( [ "Sent By", sentBy.mention, True ] )
	#else:
	#	logContents.append( [ "Sent By", "Unknown!", True ] )
	#if deletedByID:
	#	deletedBy = bot.get_user( deletedByID )
	#	logContents.append( [ "Deleted By", deletedBy.mention, True ] )
	#else:
	#	logContents.append( [ "Deleted By", "Author", True ] )
	#logContents.append( [ "Channel", "<#{0}>".format( rawMessage.channel_id ), True ] )
	#logContents.append( [ "Message", "Unknown!", False ] )

# Runs when a message is edited...
async def on_raw_message_edit( rawMessage ):
	# TO-DO: Make it work for non-cached messages!
	if not rawMessage.cached_message: return

	# TO-DO: Make this work for embed updates and other edits!
	if not "content" in rawMessage.data: return

	# Log this to the console
	logs.write( "{authorName} ({authorNick}, {authorTag}, {authorID}) edited {messageType} message {{{messageID}}} to {messageContent} ({messageLength}) in {location}.".format(
		authorName = ( "'{0}'".format( emoji.demojize( rawMessage.cached_message.author.name ) ) if rawMessage.cached_message.guild else "-HIDDEN-" ),
		authorNick = ( "'{0}'".format( emoji.demojize( rawMessage.cached_message.author.nick ) ) if not rawMessage.cached_message.author.bot and rawMessage.cached_message.guild and rawMessage.cached_message.author.nick else "-" ),
		authorTag = ( "-" if rawMessage.cached_message.webhook_id else ( "#{0}".format( rawMessage.cached_message.author.discriminator ) if rawMessage.cached_message.guild else "-HIDDEN-" ) ),
		authorID = ( rawMessage.cached_message.author.id if rawMessage.cached_message.guild else "-HIDDEN-" ),

		messageType = ( "spoken" if rawMessage.cached_message.tts else "regular" ),
		messageID = rawMessage.cached_message.id,
		messageContent = ( ", ".join( [ ( "'{0}'".format( emoji.demojize( line ) ) if line != "" else "-" ) for line in rawMessage.data[ "content" ].split( "\n" ) ] ) if rawMessage.data[ "content" ] else "-" ),
		messageLength = len( rawMessage.data[ "content" ] ),

		location = (
			( "'{serverName}' ({serverID}) -> '{categoryName}' ({categoryID}) -> '#{channelName}' ({channelID})".format(
				serverName = emoji.demojize( rawMessage.cached_message.guild.name ),
				serverID = rawMessage.cached_message.guild.id,
				
				categoryName = emoji.demojize( rawMessage.cached_message.channel.category.name ),
				categoryID = rawMessage.cached_message.channel.category.id,

				channelName = emoji.demojize( rawMessage.cached_message.channel.name ),
				channelID = rawMessage.cached_message.channel.id
			) if rawMessage.cached_message.channel.category else "'{serverName}' ({serverID}) -> '#{channelName}' ({channelID})".format(
				serverName = emoji.demojize( rawMessage.cached_message.guild.name ),
				serverID = rawMessage.cached_message.guild.id,
				
				channelName = emoji.demojize( rawMessage.cached_message.channel.name ),
				channelID = rawMessage.cached_message.channel.id
			) ) if rawMessage.cached_message.guild else "direct messages"
		)
	) )

	# Ignore Direct Messages
	if not rawMessage.cached_message.guild: return

	# Ignore bots and webhooks
	if rawMessage.cached_message.author.bot or rawMessage.cached_message.webhook_id: return

	# Ignore the history channel
	if rawMessage.cached_message.channel.id == HISTORY_CHANNEL_ID: return

	# Ignore private channels
	if rawMessage.cached_message.channel.overwrites_for( rawMessage.cached_message.guild.default_role ).pair()[ 1 ].view_channel == True: return

	# Create a list for the embed fields
	logFields = [
		[ "Author", rawMessage.cached_message.author.mention, True ],
		[ "Channel", rawMessage.cached_message.channel.mention, True ],
		[ "Jump", "[[Click]]({0})".format( rawMessage.cached_message.jump_url ), True ]
	]

	# Add the embed field for the old content, if applicable
	if len( rawMessage.cached_message.clean_content ) > 0:
		logFields.append( [ "Old Message", history.cleanMessage( rawMessage.cached_message ), False ] )
	else:
		logFields.append( [ "Old Message", "Content not displayable.", False ] )

	# Add the embed field for the new content, if applicable
	# TO-DO: This needs to be human friendly/clean content too!
	if len( rawMessage.data[ "content" ] ) > 0:
		logFields.append( [ "New Message", history.cleanMessage( rawMessage.data[ "content" ] ), False ] )
	else:
		logFields.append( [ "New Message", "Content not displayable.", False ] )

	# Log this event in the history channel
	await history.send( rawMessage.cached_message.guild, HISTORY_CHANNEL_ID, "Message Edited", logFields )

async def on_member_join( member ):
	# TO-DO: logs.write() event for this!

	await primaryServer.system_channel.send( ":wave_tone1: {memberMention} joined the community!".format(
		memberMention = member.mention
	), allowed_mentions = discord.AllowedMentions( users = True ) )

	print( member.avatar )

	await history.send( member.guild, HISTORY_CHANNEL_ID, "Member Joined", [
		[ "Member", member.mention, True ],
		[ "Account Created", "{time:%A} {time:%-d}{daySuffix} {time:%B} {time:%Y} at {time:%-H}:{time:%M} {time:%Z}".format(
			time = member.created_at,
			daySuffix = helpers.daySuffix( member.created_at.day )
		), True ]
	], str( member.avatar ) )

async def on_member_update( oldMember, newMember ):
	if oldMember.pending == True and newMember.pending == False:
		# TO-DO: logs.write() event for this!
		await newMember.add_roles( primaryServer.get_role( YEAR_2022_ROLE_ID ), reason = "Member joined in 2022." )
		# TO-DO: Grant previous roles the user had (if any)!

async def on_member_remove( member ):
	# TO-DO: logs.write() event for this!

	await primaryServer.system_channel.send( "{memberName}#{memberTag} left the community.".format(
		memberName = member.name,
		memberTag = member.discriminator
	) )
 
	totalSeconds = ( datetime.datetime.now( datetime.timezone.utc ) - member.joined_at ).total_seconds()

	minutes, seconds = divmod( totalSeconds, 60 )
	hours, minutes = divmod( minutes, 60 )
	days, hours = divmod( hours, 24 )
	years, days = divmod( days, 365 )

	values = [
		( "years", years ),
		( "days", days ),
		( "hours", hours ),
		( "minutes", minutes ),
		( "seconds", seconds )
	]

	await history.send( member.guild, HISTORY_CHANNEL_ID, "Member Left", [
		[ "Member", member.mention, True ],
		[ "Account Created", "{time:%A} {time:%-d}{daySuffix} {time:%B} {time:%Y} at {time:%-H}:{time:%M} {time:%Z}".format(
			time = member.created_at,
			daySuffix = helpers.daySuffix( member.created_at.day )
		), True ],
		[ "Stayed For", ", ".join( "{0} {1}".format( round( value ), suffix ) for suffix, value in values if value ) + ".", True ]
	], str( member.avatar ) )

async def on_guild_update( oldServer, newServer ):
	if oldServer.system_channel_flags.join_notifications != newServer.system_channel_flags.join_notifications: return

	serverTemplate = ( await newServer.templates() )[ 0 ]
	await serverTemplate.sync()
	logs.write( "Synced template '{templateName}' ({templateCode}) due to server update event.".format(
		templateName = serverTemplate.name,
		templateCode = serverTemplate.code
	) )

async def on_guild_channel_create( channel ):
	serverTemplate = ( await channel.guild.templates() )[ 0 ]
	await serverTemplate.sync()
	logs.write( "Synced template '{templateName}' ({templateCode}) due to channel create event.".format(
		templateName = serverTemplate.name,
		templateCode = serverTemplate.code
	) )

async def on_guild_channel_delete( channel ):
	serverTemplate = ( await channel.guild.templates() )[ 0 ]
	await serverTemplate.sync()
	logs.write( "Synced template '{templateName}' ({templateCode}) due to channel delete event.".format(
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
	logs.write( "Synced template '{templateName}' ({templateCode}) due to channel update event.".format(
		templateName = serverTemplate.name,
		templateCode = serverTemplate.code
	) )

async def on_guild_role_create( role ):
	serverTemplate = ( await role.guild.templates() )[ 0 ]
	await serverTemplate.sync()
	logs.write( "Synced template '{templateName}' ({templateCode}) due to role create event.".format(
		templateName = serverTemplate.name,
		templateCode = serverTemplate.code
	) )

async def on_guild_role_delete( role ):
	serverTemplate = ( await role.guild.templates() )[ 0 ]
	await serverTemplate.sync()
	logs.write( "Synced template '{templateName}' ({templateCode}) due to role delete event.".format(
		templateName = serverTemplate.name,
		templateCode = serverTemplate.code
	) )

async def on_guild_role_update( oldRole, newRole ):
	serverTemplate = ( await newRole.guild.templates() )[ 0 ]
	await serverTemplate.sync()
	logs.write( "Synced template '{templateName}' ({templateCode}) due to role update event.".format(
		templateName = serverTemplate.name,
		templateCode = serverTemplate.code
	) )

async def on_application_command( data ):
	global anonymousCooldowns

	print( "on_application_command", data )

	# TO-DO: Make this work in direct messages!
	if "guild_id" not in data:
		return await helpers.respondToInteraction( data, 4, {
			"content": "Sorry, I do not work in Direct Messages yet! Please stick to using my commands in the server for now.",
			"flags": 64
		} )

	# Fetch common properties and store them
	server = bot.get_guild( int( data[ "guild_id" ] ) )
	channel = server.get_channel( int( data[ "channel_id" ] ) )
	member = server.get_member( int( data[ "member" ][ "user" ][ "id" ] ) )
	command = data[ "data" ][ "name" ]

	# Log this event
	#logs.write( "{memberName} ({memberNick}, {memberTag}, {memberID}) used application command '{commandName}' ({commandID}, {interactionID}) with options [{commandOptions}] in {location}.".format( ) )

	if command == "activity":
		if not member.voice:
			logs.write( "{memberName}#{memberTag} attempted to start a voice activity without being in a voice channel.".format(
				memberName = member.name,
				memberTag = member.discriminator
			) )

			return await helpers.respondToInteraction( data, 4, {
				"content": "You first need to join a voice channel to start an activity!",
				"flags": 64
			} )

		if member.voice.channel.type != discord.ChannelType.voice:
			logs.write( "{memberName}#{memberTag} attempted to start a voice activity without being in a regular voice channel.".format(
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

		logs.write( "{memberName}#{memberTag} started voice activity {activityID} in voice channel {channelID}: discord.gg/{inviteCode}.".format(
			memberName = member.name,
			memberTag = member.discriminator,
			activityID = data[ "data" ][ "options" ][ 0 ][ "value" ],
			channelID = member.voice.channel.id,
			inviteCode = inviteResponse.json()[ "code" ]
		) )

	elif command == "minecraft":
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

				color = server.me.color

				if "image" in options:
					thumbnailDownloadPath = await helpers.downloadFile( options[ "image" ] )
					dominantColorRed, dominantColorGreen, dominantColorBlue = colorthief.ColorThief( thumbnailDownloadPath ).get_color( quality = 3 )
					color = ( dominantColorRed * 65536 ) + ( dominantColorGreen * 256 ) + dominantColorBlue

				rightNowUTC = datetime.datetime.now( datetime.timezone.utc )

				offerMessagePayload = {
					"embeds": [ {
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
							"text": "Offer posted on {rightNow:%A} {rightNow:%-d}{daySuffix} {rightNow:%B} {rightNow:%Y} at {rightNow:%-H}:{rightNow:%M} {rightNow:%Z}.".format(
								rightNow = rightNowUTC,
								daySuffix = helpers.daySuffix( rightNowUTC.day )
							),
							"icon_url": "https://i.imgur.com/WyrN3ml.png"
						}
					} ],
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

	elif command == "anonymous":
		anonymousChannel = server.get_channel( ANONYMOUS_CHANNEL_ID )
		options = { option[ "name" ]: option[ "value" ] for option in data[ "data" ][ "options" ][ 0 ][ "options" ] }

		if data[ "data" ][ "options" ][ 0 ][ "name" ] == "say":
			lurkerRole = server.get_role( LURKER_ROLE_ID )
			mutedRole = server.get_role( MUTED_ROLE_ID )
			rightNow = datetime.datetime.now( datetime.timezone.utc ).timestamp()

			if lurkerRole in member.roles:
				return await helpers.respondToInteraction( data, 4, {
					"content": ":interrobang: The <#{0}> channel cannot be used by lurkers!".format( anonymousChannel.id ),
					"flags": 64
				} )

			if mutedRole in member.roles:
				return await helpers.respondToInteraction( data, 4, {
					"content": ":interrobang: The <#{0}> channel cannot be used by muted members!".format( anonymousChannel.id ),
					"flags": 64
				} )

			if str( member.id ) in anonymousCooldowns and rightNow < anonymousCooldowns[ str( member.id ) ]:
				return await helpers.respondToInteraction( data, 4, {
					"content": ":interrobang: Wait a few seconds before sending another <#{0}> message.".format( anonymousChannel.id ),
					"flags": 64
				} )

			await helpers.respondToInteraction( data, 5, {
				"content": "",
				"flags": 64
			} )

			anonymousCooldowns[ str( member.id ) ] = rightNow + 3
			totalMessageCount = anonymousDatabaseCursor.execute( "SELECT COUNT( Identifier ) FROM Messages" ).fetchone()[ 0 ]
			anonymousWebhook = ( await anonymousChannel.webhooks() )[ 0 ]

			newMessage = await anonymousWebhook.send(
				content = options[ "message" ],
				username = "#{0:,}".format( totalMessageCount + 1 ),
				avatar_url = "https://cdn.discordapp.com/embed/avatars/{0}.png".format( random.randint( 0, 5 ) ),
				wait = True
			)

			hashedSender = hashlib.sha512( "{0}{1}{2}".format( os.environ[ "ANONYMOUS_SALT" ], member.id, newMessage.id ).encode() ).hexdigest()
			anonymousDatabaseCursor.execute( "INSERT INTO Messages VALUES ( ?, ? )", ( newMessage.id, hashedSender ) )
			anonymousDatabaseConnection.commit()

			return await helpers.httpRequest( "PATCH", "https://discord.com/api/v9/webhooks/{applicationID}/{interactionToken}/messages/@original".format(
				applicationID = data[ "application_id" ],
				interactionToken = data[ "token" ]
			), headers = {
				"Accept": "application/json",
				"Authorization": "Bot {0}".format( os.environ[ "BOT_TOKEN" ] ),
				"X-Audit-Log-Reason": "Updating an interaction response."
			}, json = {
				"content": "<:Tick:851511077942460427> Your message has been sent!",
				"flags": 64
			} )

		elif data[ "data" ][ "options" ][ 0 ][ "name" ] == "delete":
			if not options[ "id" ].isdigit():
				return await helpers.respondToInteraction( data, 4, {
					"content": ":interrobang: That is not a valid message ID!",
					"flags": 64
				} )

			try:
				theMessage = await channel.fetch_message( int( options[ "id" ] ) )
			except discord.NotFound:
				return await helpers.respondToInteraction( data, 4, {
					"content": ":interrobang: No message with that ID exists!",
					"flags": 64
				} )
			else:
				attemptedHashedSender = hashlib.sha512( "{0}{1}{2}".format( os.environ[ "ANONYMOUS_SALT" ], member.id, theMessage.id ).encode() ).hexdigest()
				realHashedSender = anonymousDatabaseCursor.execute( "SELECT Sender FROM Messages WHERE Identifier = ?", ( theMessage.id, ) ).fetchone()[ 0 ]

				if attemptedHashedSender != realHashedSender:
					return await helpers.respondToInteraction( data, 4, {
						"content": ":interrobang: You cannot delete messages that you did not send!",
						"flags": 64
					} )

				try:
					await theMessage.delete()

					anonymousDatabaseCursor.execute( "UPDATE Messages SET Sender = NULL WHERE Identifier = ?", ( theMessage.id, ) )
					anonymousDatabaseConnection.commit()
				except Exception as exception:
					await helpers.respondToInteraction( data, 4, {
						"content": ":interrobang: Something went wrong while attempting to delete the message!",
						"flags": 64
					} )
				else:
					return await helpers.respondToInteraction( data, 4, {
						"content": "<:Tick:851511077942460427> Your message has been deleted!",
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
	print( payload[ "t" ] )

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
	bot.event( on_raw_message_delete )
	bot.event( on_raw_message_edit )
	bot.event( on_member_join )
	bot.event( on_member_update )
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
	logs.write( "Registered post-ready event handlers." )

	# Log a message to the console
	logs.write( "Logged in as '{botName}' (#{botTag}, {botID}) on {serverCount} server(s): {serverList}.".format(
		botName = bot.user.name,
		botTag = bot.user.discriminator,
		botID = bot.user.id,
		serverCount = len( bot.guilds ),
		serverList = ( ", ".join( [ "'{serverName}' ({serverID})".format(
			serverName = emoji.demojize( server.name ),
			serverID = server.id
		) for server in bot.guilds ] ) )
	) )

	# If this is the first time running
	if not primaryServer:

		# Store the primary server instance for later use
		primaryServer = bot.get_guild( PRIMARY_SERVER_ID )
		logs.write( "The primary server is '{serverName}' ({serverID}).".format(
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
		logs.write( "Disabled default join messages for '{serverName}' ({serverID}).".format(
			serverName = emoji.demojize( primaryServer.name ),
			serverID = primaryServer.id
		) )

		# Cache the current state of the Audit Log
		await history.cacheAuditLog( primaryServer.id, 100, 72 )
		logs.write( "Cached the last 100 message deletion Audit Log events for '{serverName}' ({serverID}).".format(
			serverName = emoji.demojize( primaryServer.name ),
			serverID = primaryServer.id
		) )

	# Set the bot's current activity
	await bot.change_presence( activity = discord.Activity(
		name = "chillhop & lofi.",
		type = discord.ActivityType.listening
	) )
	logs.write( "Current activity set to '{activityType}' '{activityName}'.".format(
		activityType = primaryServer.me.activity.type.name.capitalize(),
		activityName = primaryServer.me.activity.name
	) )

	# Log a message to the console
	logs.write( "Ready!" )

# Register pre-ready event handlers
bot.event( on_connect )
bot.event( on_disconnect )
bot.event( on_resumed )
bot.event( on_ready )
logs.write( "Registered pre-ready event handlers." )

try:
	logs.write( "Connecting..." )
	bot.loop.run_until_complete( bot.start( os.environ[ "BOT_TOKEN" ] ) )
except KeyboardInterrupt:
	logs.write( "Stopping..." )

	# Remove pre-ready event handlers
	del bot.on_connect
	del bot.on_disconnect
	del bot.on_resumed
	del bot.on_ready
	logs.write( "Removed pre-ready event handlers." )

	# Remove post-ready event handlers
	del bot.on_message
	del bot.on_raw_message_delete
	del bot.on_raw_message_edit
	del bot.on_member_join
	del bot.on_member_update
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
	logs.write( "Removed post-ready event handlers." )

	# Close the relay
	#relay.close()
	#logs.write( "Closed the relay socket in '{socketPath}'.".format(
	#	socketPath = relay.path
	#) )

	anonymousDatabaseConnection.close()

	# Enable default join notifications on the server
	primaryServer = bot.get_guild( PRIMARY_SERVER_ID ) # Fetch again in-case we never got to the ready event
	systemChannelFlags = primaryServer.system_channel_flags
	systemChannelFlags.join_notifications = True
	bot.loop.run_until_complete( primaryServer.edit(
		system_channel_flags = systemChannelFlags,
		reason = "Enable default join messages."
	) )
	logs.write( "Enabled default join messages for '{serverName}' ({serverID}).".format(
		serverName = emoji.demojize( primaryServer.name ),
		serverID = primaryServer.id
	) )

	bot.loop.run_until_complete( bot.change_presence( status = discord.Status.offline ) )
	logs.write( "Cleared current activity and set status to offline." )

	# Stop logging
	logs.stop()

	bot.loop.run_until_complete( bot.close() )
finally:
	bot.loop.close()

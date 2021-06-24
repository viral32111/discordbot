# Import dependencies
import datetime, re, os
import discord, emoji
import helpers

auditLogCache = None

async def cacheAuditLog( guildID, entryLimit, actionType ):
	global auditLogCache
	response = await helpers.httpRequest( "GET", "https://discord.com/api/v9/guilds/{guildID}/audit-logs".format(
		guildID = guildID
	), params = {
		"limit": entryLimit,
		"action_type": actionType
	}, headers = {
		"Accept": "application/json",
		"Authorization": "Bot {0}".format( os.environ[ "BOT_TOKEN" ] ),
		"User-Agent": "viral32111's discord bot (https://viral32111.com/contact; contact@viral32111.com)",
		"From": "contact@viral32111.com"
	} )
	response.raise_for_status()
	results = response.json()
	auditLogCache = { entry[ "id" ]: entry[ "options" ][ "count" ] for entry in results[ "audit_log_entries" ] }

# Converts a message into a more human-friendly format for logging in an embed
def cleanMessage( message ):

	# Was the provided argument just a string?
	if isinstance( message, str ):

		# Start with whatever was provided
		content = message

	# It should be a Discord message object
	else:

		# Start with the normal content
		content = message.content

		# Clean text channel mentions
		for textChannel in message.channel_mentions:
			content = content.replace( "<#{0}>".format( textChannel.id ), "#{0}".format( textChannel.name ) )

		# Clean member (user if direct message) mentions
		for member in message.mentions:
			content = content.replace( "<@{0}>".format( member.id ), "@{0}".format( member.display_name ) )
			content = content.replace( "<@!{0}>".format( member.id ), "@{0}".format( member.display_name ) )

		# Clean role mentions
		for role in message.role_mentions:
			content = content.replace( "<@&{0}>".format( role.id ), "@{0}".format( role.name ) )

	# Escape codeblocks
	content = re.sub( r"`{3}", r"\`\`\`", content )

	# Clean custom emojis
	content = re.sub( r"<a?:(\w+):(\d+)>", r":\1:", content )

	# Clean unicode emojis
	content = emoji.demojize( content )

	# Shorten it with an elipsis if needed
	content = ( content if len( content ) <= 1024 else content[ :( 1024 - 6 - 3 ) ] + "..." ) # -6 for code block, -3 for elipsis dots

	# Return the final result in a codeblock
	return "```{0}```".format( content )

def formatAttachments( attachments ):
	return ( "\n".join( [ "[{attachmentName} {attachmentDimensions}({attachmentSize} KiB)]({attachmentURL}) [[Cache]]({attachmentProxyURL})".format(
		attachmentName = attachment.filename,
		attachmentSize = round( attachment.size / 1024, 2 ),
		attachmentDimensions = ( "({attachmentWidth}x{attachmentHeight}) ".format(
			attachmentWidth = attachment.width,
			attachmentHeight = attachment.height
		) if attachment.width else "" ),
		attachmentURL = attachment.url,
		attachmentProxyURL = attachment.proxy_url
	) for attachment in message.attachments ] ) )

async def fetchMessageDeleter( guildID, channelID, authorID ):
	rightNow = datetime.datetime.now( datetime.timezone.utc )
	fiveSecondsAgo = rightNow - datetime.timedelta( seconds = 5 )

	response = await helpers.httpRequest( "GET", "https://discord.com/api/v9/guilds/{guildID}/audit-logs".format(
		guildID = guildID
	), params = {
		"limit": 100,
		"action_type": 72 # MESSAGE_DELETE
	}, headers = {
		"Accept": "application/json",
		"Authorization": "Bot {0}".format( os.environ[ "BOT_TOKEN" ] ),
		"User-Agent": "viral32111's discord bot (https://viral32111.com/contact; contact@viral32111.com)",
		"From": "contact@viral32111.com"
	} )

	response.raise_for_status()
	results = response.json()

	for entry in results[ "audit_log_entries" ]:
		if int( entry[ "options" ][ "channel_id" ] ) != channelID: continue
		
		if authorID:
			if int( entry[ "target_id" ] ) != authorID: continue

		when = datetime.datetime.fromtimestamp( ( ( int( entry[ "id" ] ) >> 22 ) + 1420070400000 ) / 1000, tz = datetime.timezone.utc )

		if when > fiveSecondsAgo:
			auditLogCache[ entry[ "id" ] ] = entry[ "options" ][ "count" ]

			if authorID:
				return int( entry[ "user_id" ] )
			else:
				return int( entry[ "user_id" ] ), int( entry[ "target_id" ] )
		else:
			if entry[ "options" ][ "count" ] > auditLogCache[ entry[ "id" ] ]:
				auditLogCache[ entry[ "id" ] ] = entry[ "options" ][ "count" ]

				if authorID:
					return int( entry[ "user_id" ] )
				else:
					return int( entry[ "user_id" ] ), int( entry[ "target_id" ] )

			auditLogCache[ entry[ "id" ] ] = entry[ "options" ][ "count" ]

	if authorID:
		return authorID
	else:
		return authorID, authorID

# Send an event to the #history channel
async def send( server, channelID, title, fields ):
	logsChannel = server.get_channel( channelID )
	rightNow = datetime.datetime.now( datetime.timezone.utc )

	logEmbed = discord.Embed(
		title = title,
		color = server.me.color
	)

	for field in fields:
		logEmbed.add_field(
			name = field[ 0 ],
			value = field[ 1 ],
			inline = field[ 2 ]
		)

	logEmbed.set_footer(
		text = "{datetime:%A} {datetime:%-d}{daySuffix} {datetime:%B} {datetime:%Y} at {datetime:%-H}:{datetime:%M}:{datetime:%S} {datetime:%Z}".format(
			datetime = rightNow,
			daySuffix = helpers.daySuffix( rightNow.day )
		)
	)

	await logsChannel.send( embed = logEmbed )
# TO-DO: Discord to Minecraft relay - Datagram unix sockets, steal bridge code
# TO-DO: #anonymous relay - Client-only slash commands?
# TO-DO: #market channel buy/sell listings for the Minecraft server
# TO-DO: Logging for every gateway event.
# TO-DO: Basic music bot to replace Groovy.
# TO-DO: /minecraft slash command to fetch Minecraft server info & status.
# TO-DO: Store member information and statistics in SQLite database.
# TO-DO: Repost detection.

import os, functools, socket, json, re, datetime, tempfile, mimetypes
import discord, requests, emoji, colorthief
import relay, helpers

communityGuild = 240167618575728644

bot = discord.Client( intents = discord.Intents.all(), allowed_mentions = discord.AllowedMentions.none() )
relay.Setup( "discordbot", bot.loop )
helpers._eventLoop = bot.loop

async def on_ready():
	global communityGuild

	communityGuild = bot.get_guild( communityGuild )

	systemChannelFlags = communityGuild.system_channel_flags
	systemChannelFlags.join_notifications = False
	await communityGuild.edit( system_channel_flags = systemChannelFlags, reason = "Disable default welcome messages now that I'm online." )

	await bot.change_presence( activity = discord.Activity( name = "all of you.", type = discord.ActivityType.watching ) )

	# TO-DO: Minecraft account details in #market offers!
	#minecraftUUID = "a51dccb57ffa426b833b1a9ce3a31446"
	#minecraftUsername = "viral32111"
	#"name": "{userName}#{userTag} {minecraftUsername}".format(
	#	userName = discordUser.name,
	#	userTag = discordUser.discriminator,
	#	minecraftUsername = ( "({0})".format( minecraftUsername ) if minecraftUUID else "" )
	#),
	#if minecraftUUID:
	#	offerMessagePayload[ "components" ][ 0 ][ "components" ].insert( 0, {
	#		"type": 2,
	#		"style": 5,
	#		"label": "Minecraft Profile",
	#		"url": "https://namemc.com/profile/{0}".format( minecraftUUID ),
	#		"disabled": False
	#	} )

	print( "Ready!" )

async def on_message( message ):
	# TO-DO: Embeds, TTS, System, Replies, Crosspost, Activity/Application, Bots/Webhooks, DMs/Guilds
	# 'viral32111' (-, #2016, 480764191465144331) sent message 'hello' ['example.jpg' (image/jpeg, 1348213B, 1920px, 1080px, 790567563321933835), ] (849575982988918854) in '#text' (822533400610471946)
	print( "'{memberName}' ({memberNick}, #{memberTag}, {memberID}) sent message {messageContent} [{attachments}] ({messageLength}, {messageID}) in {channel}".format(
		memberName = emoji.demojize( message.author.name ),
		memberNick = ( "'{0}'".format( emoji.demojize( message.author.nick ) ) if not message.author.bot and message.author.nick else "-" ),
		memberTag = message.author.discriminator,
		memberID = message.author.id,

		messageContent = ( ", ".join( [ ( "'{0}'".format( emoji.demojize( line ) ) if line != "" else "-" ) for line in message.content.split( "\n" ) ] ) if message.content else "-" ),
		attachments = (
			( ", ".join( [ "'{attachmentName}' ({attachmentType}, {attachmentSize}B, {attachmentWidth}, {attachmentHeight}, {attachmentID})".format(
				attachmentName = attachment.filename,
				attachmentType = ( attachment.content_type or "-" ),
				attachmentSize = attachment.size,
				attachmentWidth = ( "{0}px".format( attachment.width ) if attachment.width else "-" ),
				attachmentHeight = ( "{0}px".format( attachment.height ) if attachment.height else "-" ),
				attachmentID = attachment.id
			) for attachment in message.attachments ] ) ) if len( message.attachments ) > 0 else "-"
		),
		messageLength = len( message.content ),
		messageID = message.id,

		channel = (
			"'{categoryName}' ({categoryID}) -> '#{channelName}' ({channelID})".format(
				categoryName = emoji.demojize( message.channel.category.name ),
				categoryID = message.channel.category.id,

				channelName = emoji.demojize( message.channel.name ),
				channelID = message.channel.id
			) if message.channel.category else "'#{channelName}' ({channelID})".format(
				channelName = emoji.demojize( message.channel.name ),
				channelID = message.channel.id
			)
		)
	) )

	if message.channel.id == 851437359237169183 and not message.author.bot and len( message.content ) > 0:
		try:
			await relay.Send( relay.Type.Message, {
				"username": emoji.demojize( message.author.display_name ),
				"content": emoji.demojize( message.clean_content.replace( "\n", " " ) ),
				"color": message.author.color.value
			}, "minecraft" )
		except Exception as exception:
			await message.reply( ":interrobang: Your message could not be sent due to an internal error!" )
			raise exception

async def on_member_join( member ):
	channel = bot.get_channel( 240167618575728644 )

	if re.search( r"twitter\.com\/h0nde", member.name, flags = re.IGNORECASE ):
		lurkerRole = communityGuild.get_role( 807559722127458304 )
		await member.add_roles( lurkerRole, reason = "Dumb spam bot >:(" )
		await channel.send( ":anger: {memberMention} is a dumb spam bot.".format( memberMention = member.mention ) )
	else:
		await channel.send( ":wave_tone1: {memberMention} joined the community!".format( memberMention = member.mention ) )

async def on_member_remove( member ):
	channel = bot.get_channel( 240167618575728644 )
	await channel.send( "{memberName}#{memberTag} left the community.".format(
		memberName = member.name,
		memberTag = member.discriminator
	) )

async def on_guild_channel_update( oldChannel, newChannel ):
	if newChannel.id == 826908363392680026 and newChannel.name != "Stage":
		await newChannel.edit( name = "Stage", reason = "Do not rename this channel! >:(" )

async def on_application_command( data ):
	if "guild_id" not in data:
		print( "{userName}#{userTag} attempted to use my commands in Direct Messages".format(
			userName = data[ "user" ][ "username" ],
			userTag = data[ "user" ][ "discriminator" ],
		) )

		return await helpers.respondToInteraction( data, 4, {
			"content": "Sorry, I do not work in Direct Messages yet! Please stick to using my commands in the server for now.",
			"flags": 64
		} )

	guild = bot.get_guild( int( data[ "guild_id" ] ) )
	channel = guild.get_channel( int( data[ "channel_id" ] ) )
	member = guild.get_member( int( data[ "member" ][ "user" ][ "id" ] ) )

	if data[ "data" ][ "name" ] == "activity":
		if not member.voice:
			print( "{memberName}#{memberTag} attempted to start a voice activity without being in a voice channel".format(
				memberName = member.name,
				memberTag = member.discriminator
			) )

			return await helpers.respondToInteraction( data, 4, {
				"content": "You first need to join a voice channel to start an activity!",
				"flags": 64
			} )

		if member.voice.channel.type != discord.ChannelType.voice:
			print( "{memberName}#{memberTag} attempted to start a voice activity without being in a regular voice channel".format(
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

		print( "{memberName}#{memberTag} started voice activity {activityID} in voice channel {channelID}: discord.gg/{inviteCode}".format(
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
								daySuffix = daySuffix( rightNowUTC.day )
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

				marketChannelID = 852114085750636584

				offerMessageResponse = await helpers.httpRequest( "POST", "https://discord.com/api/v9/channels/{channelID}/messages".format(
					channelID = marketChannelID
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
						channelID = marketChannelID,
						messageID = offerMessage[ "id" ],
						messageLink = "https://discord.com/channels/{serverID}/{channelID}/{messageID}".format(
							serverID = guild.id,
							channelID = marketChannelID,
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

	return await helpers.respondToInteraction( data, 6, None )

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

bot.event( on_ready )
bot.event( on_message )
bot.event( on_member_join )
bot.event( on_member_remove )
bot.event( on_guild_channel_update )
bot.event( on_application_command )
bot.event( on_message_component )
bot.event( on_socket_response )

try:
	print( "Connecting..." )
	bot.loop.run_until_complete( bot.start( os.environ[ "BOT_TOKEN" ] ) )
except KeyboardInterrupt:
	print( "Stopping..." )

	os.remove( "/var/run/relay/discordbot.sock" )

	guild = bot.get_guild( 240167618575728644 )
	systemChannelFlags = guild.system_channel_flags
	systemChannelFlags.join_notifications = True
	bot.loop.run_until_complete( guild.edit( system_channel_flags = systemChannelFlags, reason = "Enable default welcome messages now that I'm offline." ) )

	bot.loop.run_until_complete( bot.change_presence( status = discord.Status.offline ) )
	bot.loop.run_until_complete( bot.close() )
finally:
	bot.loop.close()

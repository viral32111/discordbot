# TO-DO: Discord to Minecraft relay - Datagram unix sockets, steal bridge code
# TO-DO: #anonymous relay - Client-only slash commands?
# TO-DO: #market channel buy/sell listings for the Minecraft server
# TO-DO: Logging for every gateway event.
# TO-DO: Basic music bot to replace Groovy.
# TO-DO: /minecraft slash command to fetch Minecraft server info & status.

import os, functools
import discord, requests

bot = discord.Client( intents = discord.Intents.all() )

async def httpRequest( *args, **kwargs ):
	return await bot.loop.run_in_executor( None, functools.partial( requests.request, *args, **kwargs ) )

async def on_ready():
	print( "Ready!" )

	guild = bot.get_guild( 240167618575728644 )
	systemChannelFlags = guild.system_channel_flags
	systemChannelFlags.join_notifications = False
	await guild.edit( system_channel_flags = systemChannelFlags, reason = "Disable default welcome messages now that I'm online." )

	await bot.change_presence( activity = discord.Activity( name = "all of you.", type = discord.ActivityType.watching ) )

async def on_message( message ):
	# TO-DO: Embeds, TTS, System, Replies, Crosspost, Activity/Application, Bots/Webhooks, DMs/Guilds
	# 'viral32111' (-, #2016, 480764191465144331) sent message 'hello' ['example.jpg' (image/jpeg, 1348213B, 1920px, 1080px, 790567563321933835), ] (849575982988918854) in '#text' (822533400610471946)
	print( "'{memberName}' ({memberNick}, #{memberTag}, {memberID}) sent message {messageContent} [{attachments}] ({messageLength}, {messageID}) in {channel}".format(
		memberName = message.author.name,
		memberNick = ( "'{}'".format( message.author.nick ) if not message.author.bot and message.author.nick else "-" ),
		memberTag = message.author.discriminator,
		memberID = message.author.id,

		messageContent = ( ", ".join( [ ( "'{}'".format( line ) if line != "" else "-" ) for line in message.content.split( "\n" ) ] ) if message.content else "-" ),
		attachments = (
			( ", ".join( [ "'{attachmentName}' ({attachmentType}, {attachmentSize}B, {attachmentWidth}, {attachmentHeight}, {attachmentID})".format(
				attachmentName = attachment.filename,
				attachmentType = ( attachment.content_type or "-" ),
				attachmentSize = attachment.size,
				attachmentWidth = ( "{}px".format( attachment.width ) if attachment.width else "-" ),
				attachmentHeight = ( "{}px".format( attachment.height ) if attachment.height else "-" ),
				attachmentID = attachment.id
			) for attachment in message.attachments ] ) ) if len( message.attachments ) > 0 else "-"
		),
		messageLength = len( message.content ),
		messageID = message.id,

		channel = (
			"'{categoryName}' ({categoryID}) -> '#{channelName}' ({channelID})".format(
				categoryName = message.channel.category.name,
				categoryID = message.channel.category.id,

				channelName = message.channel.name,
				channelID = message.channel.id
			) if message.channel.category else "'#{channelName}' ({channelID})".format(
				channelName = message.channel.name,
				channelID = message.channel.id
			)
		)
	) )

async def on_member_join( member ):
	channel = bot.get_channel( 240167618575728644 )
	await channel.send( "{memberMention} joined the community!".format( memberMention = member.mention ), allowed_mentions = discord.AllowedMentions.none() )

async def on_member_remove( member ):
	channel = bot.get_channel( 240167618575728644 )
	await channel.send( "{memberName}#{memberTag} left the community.".format(
		memberName = member.name,
		memberTag = member.discriminator
	) )

async def on_guild_channel_update( oldChannel, newChannel ):
	if newChannel.id == 826908363392680026 and newChannel.name != "Stage":
		await newChannel.edit( name = "Stage", reason = "Do not rename this channel! >:(" )

async def on_socket_response( payload ):
	if payload[ "t" ] != "INTERACTION_CREATE": return

	if "guild_id" not in payload[ "d" ]:
		print( "{userName}#{userTag} attempted to use my commands in Direct Messages".format(
			userName = payload[ "d" ][ "user" ][ "username" ],
			userTag = payload[ "d" ][ "user" ][ "discriminator" ],
		) )

		return await httpRequest( "POST", "https://discord.com/api/v9/interactions/{interactionID}/{interactionToken}/callback".format(
			interactionID = payload[ "d" ][ "id" ],
			interactionToken = payload[ "d" ][ "token" ]
		), headers = {
			"Accept": "application/json",
			"Authorization": "Bot {0}".format( os.environ[ "BOT_TOKEN" ] ),
			"User-Agent": "viral32111's community discord bot (https://viral32111.com/contact; contact@viral32111.com)",
			"From": "contact@viral32111.com",
				"X-Audit-Log-Reason": "Attempting to use me in Direct Messages."
		}, json = {
			"type": 4,
			"data": {
				"content": "Sorry, I do not work in Direct Messages yet! Please stick to using my commands in the server for now.",
				"flags": 64
			}
		} )

	guild = bot.get_guild( int( payload[ "d" ][ "guild_id" ] ) )
	channel = guild.get_channel( int( payload[ "d" ][ "channel_id" ] ) )
	member = guild.get_member( int( payload[ "d" ][ "member" ][ "user" ][ "id" ] ) )

	if payload[ "d" ][ "data" ][ "name" ] == "activity":
		if not member.voice:
			print( "{memberName}#{memberTag} attempted to start a voice activity without being in a voice channel".format(
				memberName = member.name,
				memberTag = member.discriminator
			) )

			return await httpRequest( "POST", "https://discord.com/api/v9/interactions/{interactionID}/{interactionToken}/callback".format(
				interactionID = payload[ "d" ][ "id" ],
				interactionToken = payload[ "d" ][ "token" ]
			), headers = {
				"Accept": "application/json",
				"Authorization": "Bot {0}".format( os.environ[ "BOT_TOKEN" ] ),
				"User-Agent": "viral32111's community discord bot (https://viral32111.com/contact; contact@viral32111.com)",
				"From": "contact@viral32111.com",
				"X-Audit-Log-Reason": "Attempting to use voice activities without calling member in a voice channel."
			}, json = {
				"type": 4,
				"data": {
					"content": "You first need to join a voice channel to start an activity!",
					"flags": 64
				}
			} )

		if member.voice.channel.type != discord.ChannelType.voice:
			print( "{memberName}#{memberTag} attempted to start a voice activity without being in a regular voice channel".format(
				memberName = member.name,
				memberTag = member.discriminator
			) )

			return await httpRequest( "POST", "https://discord.com/api/v9/interactions/{interactionID}/{interactionToken}/callback".format(
				interactionID = payload[ "d" ][ "id" ],
				interactionToken = payload[ "d" ][ "token" ]
			), headers = {
				"Accept": "application/json",
				"Authorization": "Bot {0}".format( os.environ[ "BOT_TOKEN" ] ),
				"User-Agent": "viral32111's community discord bot (https://viral32111.com/contact; contact@viral32111.com)",
				"From": "contact@viral32111.com",
				"X-Audit-Log-Reason": "Attempting to use voice activities in a non-voice channel."
			}, json = {
				"type": 4,
				"data": {
					"content": "Only regular voice channels are supported!",
					"flags": 64
				}
			} )

		inviteResponse = await httpRequest( "POST", "https://discord.com/api/v9/channels/{voiceChannelID}/invites".format(
			voiceChannelID = member.voice.channel.id
		), headers = {
			"Accept": "application/json",
			"Authorization": "Bot {0}".format( os.environ[ "BOT_TOKEN" ] ),
			"User-Agent": "viral32111's community discord bot (https://viral32111.com/contact; contact@viral32111.com)",
			"From": "contact@viral32111.com",
			"X-Audit-Log-Reason": "Starting activity in a voice channel."
		}, json = {
			"max_age": 3600,
			"target_type": 2,
			"target_application_id": payload[ "d" ][ "data" ][ "options" ][ 0 ][ "value" ]
		} )

		await httpRequest( "POST", "https://discord.com/api/v9/interactions/{interactionID}/{interactionToken}/callback".format(
			interactionID = payload[ "d" ][ "id" ],
			interactionToken = payload[ "d" ][ "token" ]
		), headers = {
			"Accept": "application/json",
			"Authorization": "Bot {0}".format( os.environ[ "BOT_TOKEN" ] ),
			"User-Agent": "viral32111's community discord bot (https://viral32111.com/contact; contact@viral32111.com)",
			"From": "contact@viral32111.com",
			"X-Audit-Log-Reason": "Voice activity started."
		}, json = {
			"type": 4,
			"data": {
				"content": "[Click me to start!](<https://discord.gg/{inviteCode}>) This link will expire in 1 hour.".format( inviteCode = inviteResponse.json()[ "code" ] ),
				"allowed_mentions": { "parse": [] }
			}
		} )

		print( "{memberName}#{memberTag} started voice activity {activityID} in voice channel {voiceChannelID}: discord.gg/{inviteCode}".format(
			memberName = member.name,
			memberTag = member.discriminator,
			activityID = payload[ "d" ][ "data" ][ "options" ][ 0 ][ "value" ],
			voiceChannelID = member.voice.channel.id,
			inviteCode = inviteResponse.json()[ "code" ]
		) )

bot.event( on_ready )
bot.event( on_message )
bot.event( on_member_join )
bot.event( on_member_remove )
bot.event( on_guild_channel_update )
bot.event( on_socket_response )

try:
	print( "Connecting..." )
	bot.loop.run_until_complete( bot.start( os.environ[ "BOT_TOKEN" ] ) )
except KeyboardInterrupt:
	print( "Stopping..." )

	guild = bot.get_guild( 240167618575728644 )
	systemChannelFlags = guild.system_channel_flags
	systemChannelFlags.join_notifications = True
	bot.loop.run_until_complete( guild.edit( system_channel_flags = systemChannelFlags, reason = "Enable default welcome messages now that I'm offline." ) )

	bot.loop.run_until_complete( bot.change_presence( status = discord.Status.offline ) )
	bot.loop.run_until_complete( bot.close() )
finally:
	bot.loop.close()

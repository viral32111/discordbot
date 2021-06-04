import os
import discord

bot = discord.Client( intents = discord.Intents.all() )

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

bot.event( on_ready )
bot.event( on_message )
bot.event( on_member_join )
bot.event( on_member_remove )
bot.event( on_guild_channel_update )

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

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

##############################################
# Setup this script
##############################################

# Import variables from the main script
from __main__ import configuration, fileChecksum, USER_AGENT_HEADER, mysqlQuery, DAY_SUFFIXES, formatTimestamp, anonymousMessageHashes

# Import required modules
import slashcommands, discord, youtube_dl, requests, pytz, datetime, re, os

##############################################
# Define slash commands
##############################################

# View personal member statistics
@slashcommands.new( "View your member statistics.", guild = 240167618575728644 )
async def statistics( interaction ):

	# Fetch this member's statistics
	statistics = mysqlQuery( "SELECT Messages, Edits, Deletions FROM MemberStatistics WHERE Member = LOWER( HEX( AES_ENCRYPT( '" + str( interaction.user.id ) + "', UNHEX( SHA2( '" + os.environ[ "ENCRYPTION_STATISTICS" ] + "', 512 ) ) ) ) );" )[ 0 ]

	# Format each statistic
	messages = "{:,}".format( statistics[ 0 ] )
	edits = "{:,}".format( statistics[ 1 ] )
	deletions = "{:,}".format( statistics[ 2 ] )

	# Respond with their statistics
	await interaction.respond( ":bar_chart: You have sent a total of **" + messages + "** messages in this server, made **" + edits + "** edits to your own messages & deleted **" + deletions + "** of your own messages.\n*(Statistics from before 02/08/2020 07:01:05 UTC may not be 100% accurate)*", hidden = True )

# View the top member statistics
@slashcommands.new( "View the top member statistics.", guild = 240167618575728644 )
async def topstatistics( interaction ):

	# Fetch the top 20 member statistics
	topStatistics = mysqlQuery( "SELECT AES_DECRYPT( UNHEX( Member ), UNHEX( SHA2( '" + os.environ[ "ENCRYPTION_STATISTICS" ] + "', 512 ) ) ) AS Member, Messages, Edits, Deletions FROM MemberStatistics ORDER BY Messages DESC LIMIT 18;" )

	#guild = interaction.client.guilds[ 0 ]

	# Create a blank embed
	#embed = discord.Embed( title = "Top 20", description = "", color = guild.me.top_role.color.value )

	# Set a notice in the embed footer
	#embed.set_footer( text = "Statistics from before 02/08/2020 07:01:05 UTC may not be 100% accurate." )

	messageContent = "```\n{:<4} {:<36} {:<14} {:<16} {:<17}\n".format( "No.", "Member Name", "Messages Sent", "Messages Edited", "Messages Deleted" )
	messageContent += "{:<4} {:<36} {:<14} {:<16} {:<17}\n".format( "-" * 4, "-" * 36, "-" * 14, "-" * 16, "-" * 17 )
	counter = 1

	# Loop through each top statistic
	for statistics in topStatistics:

		# The user's ID
		userID = int( statistics[ 0 ] )

		# Try to get the user from the client's cache
		user = interaction.client.get_user( userID )

		# Fetch basic user information via an API call if the user couldn't be found in the client's cache (they probably aren't on the guild)
		if user == None: user = await interaction.client.fetch_user( userID )

		# Format each statistic
		messages = "{:,}".format( statistics[ 1 ] )
		edits = "{:,}".format( statistics[ 2 ] )
		deletions = "{:,}".format( statistics[ 3 ] )

		# Add it to the embed description
		#embed.description += "• " + ( user.mention if user in message.guild.members else str( user ) ) + ": " + messages + " messages, " + edits + " edits, " + deletions + " deletions.\n"

		messageContent += "{:<4} {:<36} {:<14} {:<16} {:<17}\n".format( str( counter ), str( user ), messages, edits, deletions )

		counter += 1

	messageContent += "\n```"

	# Respond with the embed
	await interaction.respond( messageContent, hidden = True )

# View the date & time you joined
@slashcommands.new( "View the date & time you joined", guild = 240167618575728644 )
async def joined( interaction ):

	# Fetch this date & time the member joined
	joinedAt = mysqlQuery( "SELECT FROM_UNIXTIME( AES_DECRYPT( Joined, UNHEX( SHA2( '" + os.environ[ "ENCRYPTION_MEMBERS" ] + "', 512 ) ) ) ) AS Joined FROM Members WHERE Member = AES_ENCRYPT( '" + str( interaction.user.id ) + "', UNHEX( SHA2( '" + os.environ[ "ENCRYPTION_MEMBERS" ] + "', 512 ) ) );" )[ 0 ][ 0 ]

	# Fetch the appropriate day suffix
	daySuffix = DAY_SUFFIXES.get( joinedAt.day, "th" )

	# Construct a formatting template using the day suffix
	template = "%A %-d" + daySuffix + " of %B %Y at %-H:%M:%S"

	# Get the pretty date & time
	joinedAtPretty = joinedAt.strftime( template )

	# Respond with a message
	await interaction.respond( ":date: You joined this Discord server on **" + joinedAtPretty + "**.\n*(Information from before 08/08/2020 UTC may not be 100% accurate.)*", hidden = True )

# Get the time in a specific timezone
@slashcommands.new( "Get the time in a specific timezone", options = [ slashcommands.option(
	name = "timezone",
	description = "The name of the timezone (e.g. US/Eastern).",
	type = slashcommands.option.type.string,
	required = True
) ], guild = 240167618575728644 )
async def time( interaction ):

	# Be safe!
	try:

		# Attempt to parse the timezone query
		timezone = pytz.timezone( interaction.arguments[ "timezone" ] )

	# Catch unknown timezone errors
	except pytz.exceptions.UnknownTimeZoneError:

		# Respond with a message
		await interaction.respond( ":grey_question: That doesn't appear to be a valid timezone name or identifier.", hidden = True )
		return

	# The timezone is valid
	else:

		# Get the timezone's local time from the current UTC time
		timezoneTime = datetime.datetime.now( timezone )

		# Fetch the appropriate day suffix
		daySuffix = DAY_SUFFIXES.get( timezoneTime.day, "th" )

		# Construct a formatting template using the day suffix
		template = "%A %-d" + daySuffix + " of %B %Y at %-H:%M:%S %Z (%z)"

		# Get the pretty date & time
		timezonePretty = timezoneTime.strftime( template )

		# Respond with a message
		await interaction.respond( ":calendar: " + timezonePretty, hidden = True )

# Get weather data for a location
@slashcommands.new( "Get weather data for a location", options = [ slashcommands.option(
	name = "location",
	description = "the place to get weather data for (e.g. London).",
	type = slashcommands.option.type.string,
	required = True
) ], guild = 240167618575728644 )
async def weather( interaction ):

	# Make the API request
	weatherRequest = requests.request( "GET", "https://api.openweathermap.org/data/2.5/weather", params = {
		"appid": os.environ[ "OPENWEATHERMAP_APIKEY" ],
		"units": "metric",
		"lang": "en",
		"q": interaction.arguments[ "location" ]
	}, headers = {
		"Accept": "application/json",
		"From": configuration[ "general" ][ "email" ],
		"User-Agent": USER_AGENT_HEADER
	} )

	# Was a weather result not found?
	if weatherRequest.status_code == 404:

		# Friendly message
		await interaction.respond( ":mag_right: I wasn't able to find weather data for a location with that name.", hidden = True )
		return

	# Was the request unsuccessful?
	if weatherRequest.status_code != 200:

		# Throw an error
		raise Exception( "Received non-success API response: " + str( weatherRequest.status_code ) + "\n" + str( weatherRequest.text ) )

	# Parse response
	data = weatherRequest.json()

	# Create an basic embed
	embed = discord.Embed(

		# The name of the city and the country code as the title
		title = data[ "name" ] + ", " + data[ "sys" ][ "country" ],

		# Set the color to white (more or less)
		color = 0xF4F7F7,

	)

	# Add a field to the embed for the weather
	embed.add_field( name = "Weather", value = data[ "weather" ][ 0 ][ "description" ].title(), inline = True )

	# Add a field to the embed for the temperature
	embed.add_field( name = "Temperature", value = str( data[ "main" ][ "temp" ] ) + " °C (" + str( data[ "main" ][ "feels_like" ] ) + " °C)", inline = True )

	# Add a field to the embed for the pressure
	embed.add_field( name = "Pressure", value = str( data[ "main" ][ "pressure" ] ) + " hPa", inline = True )

	# Add a field to the embed for the humidity
	embed.add_field( name = "Humidity", value = str( data[ "main" ][ "humidity" ] ) + "%", inline = True )

	# Add a field to the embed for the wind speed
	embed.add_field( name = "Wind Speed", value = str( data[ "wind" ][ "speed" ] ) + " m/s", inline = True )

	# Add a field to the embed for the sunrise
	embed.add_field( name = "Sunrise", value = formatTimestamp( data[ "sys" ][ "sunrise" ] ), inline = False )

	# Add a field to the embed for the sunset
	embed.add_field( name = "Sunset", value = formatTimestamp( data[ "sys" ][ "sunset" ] ), inline = False )

	# Set the weather icon as the thumbnail
	embed.set_thumbnail( url = "https://openweathermap.org/img/wn/" + data[ "weather" ][ 0 ][ "icon" ] + "@2x.png" )

	# Respond with the embed
	await interaction.respond( embeds = [ embed ] )

# Delete message sent in anonymous
@slashcommands.new( "Delete message sent in anonymous", options = [ slashcommands.option(
	name = "id",
	description = "ID of the message to delete.",
	type = slashcommands.option.type.string,
	required = True
) ], guild = 240167618575728644 )
async def anonymousdelete( interaction ):

	# Fetch the guild
	guild = interaction.client.guilds[ 0 ]

	# Fetch the anonymous channel
	anonymousChannel = guild.get_channel( configuration[ "channels" ][ "anonymous" ] )

	# Be safe!
	try:
		
		# Placeholder for the message ID
		messageID = None

		# Regex pattern for if they sent a message link as the argument
		messageLinkMatch = re.match( r"^https:\/\/discordapp\.com\/channels\/240167618575728644\/661694045600612352\/(\d{18})$", interaction.arguments[ "id" ] )

		# Was it a message link?
		if messageLinkMatch:

			# Set the message ID to the captured group
			messageID = messageLinkPattern.group( 1 )

		# It was not a message link
		else:

			# Set the message ID to the value of the entire argument
			messageID = interaction.arguments[ "id" ]

		# Fetch the specified message ID in the anonymous channel
		anonymousMessage = await anonymousChannel.fetch_message( int( messageID ) )

	# The message couldn't be found
	except discord.NotFound:

		# Friendly message
		await interaction.respond( ":mag_right: I wasn't able to find a <#" + str( configuration[ "channels" ][ "anonymous" ] ) + "> message with that ID.", hidden = True )
		return

	# The specified ID wasn't really an ID
	except ValueError:

		# Friendly message
		await interaction.respond( ":grey_question: That doesn't appear to be a valid message ID.", hidden = True )
		return

	# The message has been found
	else:

		# Calculate the message identifier and deletion token attempt
		messageIdentifier, deletionTokenAttempt = anonymousMessageHashes( anonymousMessage, interaction.user.id )

		# Try to see if a message with this identifier and deletion token exists
		existsResult = mysqlQuery( "SELECT EXISTS ( SELECT * FROM AnonMessages WHERE Message = '" + messageIdentifier + "' AND Token = '" + deletionTokenAttempt + "' );" )

		# Parse the results
		hasOwnership = bool( existsResult[ 0 ][ 0 ] )

		# Do they not own the message?
		if not hasOwnership:

			# Friendly message
			await interaction.respond( ":no_entry_sign: The message has not been deleted because your ownership of it could not be verified.\n(Please note, <#" + str( configuration[ "channels" ][ "anonymous" ] ) + "> messages sent before the 22nd July 2020 cannot be deleted as no ownership information exists for them.)", hidden = True )
			return

		# Delete the message from the anonymous channel
		await anonymousMessage.delete()

		# Remove the record from the database
		mysqlQuery( "DELETE FROM AnonMessages WHERE Message = '" + messageIdentifier + "' AND Token = '" + deletionTokenAttempt + "';" )

		# Friendly message
		await interaction.respond( ":white_check_mark: The message has been successfully deleted.", hidden = True )

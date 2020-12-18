###################################################################################
# Conspiracy AI - The official Discord bot for the Conspiracy Servers community.
# Copyright (C) 2016 - 2020 viral32111 (https://viral32111.com)
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
from __main__ import chatCommands, settings, fileChecksum, USER_AGENT_HEADER, mysqlQuery, secrets, DAY_SUFFIXES, formatTimestamp, anonymousMessageHashes

# Import required modules
import discord, youtube_dl, requests, pytz, datetime, re

##############################################
# Define chat commands
##############################################

# Help
@chatCommands( category = "General" )
async def help( message, arguments, client ):

	# Create a blank embed
	embed = discord.Embed( title = "", description = "", color = settings.color )

	# Add the about field to the embed
	embed.add_field(

		# The title of the field
		name = "About Us",

		# The description of the field
		value = "Conspiracy Servers is a Garry's Mod community founded by <@" + str( settings.owner ) + "> and <@213413722943651841> in early 2016. We've been going for nearly 5 years now and have always kept our non-serious, relaxed and casual approach towards our community and the servers which we run."

	)

	# Add the guidelines & rules field to the embed
	embed.add_field(

		# The title of the field
		name = "Guidelines & Rules",

		# The description of the field
		value = "If you're new here or need a refresher on our rules & guidelines then read <#410507397166006274>.",

		# Don't place this field inline with the other fields
		inline = False

	)

	# Add the chat commands field to the embed
	embed.add_field(

		# The title of the field
		name = "Chat Commands",

		# The description of the field
		value = "Type `" + settings.prefix + "commands` for a list of chat commands. Keep command usage in <#241602380569772044> to avoid cluttering the discussion channels.",

		# Don't place this field inline with the other fields
		inline = False

	)

	# Add the contacting staff field to the embed
	embed.add_field(

		# The title of the field
		name = "Contacting Staff",

		# The description of the field
		value = "You can reach out to our staff by direct messaging anyone with the <@&507323152737763352>, <@&613124236101419019>, <@&748809314290106389> or <@&519273212807348245> role.",

		# Don't place this field inline with the other fields
		inline = False

	)

	# Respond with this embed
	return { "embed": embed }

# Link Steam account
@chatCommands( category = "General" )
async def link( message, arguments, client ):

	# Respond with a simple message
	return { "content": ":link: Visit <https://conspiracyservers.com/link> to link your Steam account." }

# View available commands
@chatCommands( category = "General", aliases = [ "cmds" ] )
async def commands( message, arguments, client ):

	# A dictionary to hold all chat commands by their category
	availableChatCommands = {}

	# Loop through all registered chat commands
	for command, metadata in chatCommands:

		# Skip aliases by checking if the command is in it's own alias dictionary
		if command in metadata.aliases: continue

		# Add the category to the dictionary if this command's category is not already in it
		if metadata.category not in availableChatCommands: availableChatCommands[ metadata.category ] = {}

		# Add this command as the key and it's aliases as the value to the dictionary
		availableChatCommands[ metadata.category ][ command ] = metadata.aliases

	# Create a basic embed
	embed = discord.Embed( title = "Chat Commands", description = "", color = settings.color )

	# Loop through all categories & their commands
	for category, commands in availableChatCommands.items():

		# Placeholder for the value of this embed field
		value = ""

		# Loop through all aliases of this command in this category
		for command, aliases in commands.items():

			# Construct a string out of the list of command aliases
			aliasesString = " (" + ", ".join( [ "`" + settings.prefix + alias + "`" for alias in aliases ] ) + ")"

			# Append the command name and it's aliases (if any are available) to the final embed description
			value += "• `" + settings.prefix + command + "`" + ( aliasesString if len( aliases ) > 0 else "" ) + "\n"

		# Add the field to the embed for this category
		embed.add_field( name = category, value = value, inline = False )

	# Respond with this embed
	return { "embed": embed }

# Fetch an anime/manga from MyAnimeList
@chatCommands( category = "General", aliases = [ "mal", "anime", "manga" ] )
async def myanimelist( message, arguments, client ):

	# Send a message if no arguments were provided
	if len( arguments ) < 1: return { "content": ":grey_exclamation: You must specify the name of an anime to fetch information about." }

	# Construct the request URL
	animeQuery = "%20".join( arguments )
	apiURL = "https://api.jikan.moe/v3/search/anime?q=" + animeQuery

	# Make the request to the API
	malRequest = requests.get( apiURL, headers = {
		"Accept": "application/json",
		"User-Agent": USER_AGENT_HEADER,
		"From": settings.email
	} )
	
	# Was the request unsuccessful?
	if malRequest.status_code != 200:

		# Throw an error
		raise Exception( "Received non-success API response: " + str( malRequest.status_code ) + "\n" + str( malRequest.text ) )

	# Parse response
	data = malRequest.json()

	# Was there no search results returned?
	if len( data[ "results" ] ) < 1:

		# Friendly message
		return { "content": ":mag_right: I wasn't able to find an anime with that name." }

	# We want the first result (likely the best match)
	anime = data[ "results" ][ 0 ]

	# Create an embed with the anime information
	embed = discord.Embed(
		title = anime[ "title" ],
		description = anime[ "synopsis" ],
		url = anime[ "url" ],
		color = 0x2E51A2
	)

	# Set the embed thumbnail to the anime's cover art
	embed.set_thumbnail(
		url = anime[ "image_url" ]
	)

	# Add a field for the user score
	embed.add_field(
		name = "Score",
		value = str( anime[ "score" ] ),
		inline = True
	)

	# Add a field for the age rating
	embed.add_field(
		name = "Rating",
		value = anime[ "rated" ],
		inline = True
	)

	# Add a field for the amount of episodes
	embed.add_field(
		name = "Episodes",
		value = str( anime[ "episodes" ] ),
		inline = True
	)

	# Add a field for the type (TV, manga, anime, etc)
	embed.add_field(
		name = "Type",
		value = anime[ "type" ],
		inline = True
	)

	# Add a field for if it is currently airing
	embed.add_field(
		name = "Currently Airing",
		value = ( "Yes" if anime[ "airing" ] == True else "No" ),
		inline = True
	)

	# Store the amount of additional results
	additionalResultsCount = len( data[ "results" ] ) - 1

	# Were there any additional results?
	if additionalResultsCount > 0:

		# Set the embed's footer to inform them
		embed.set_footer( text = str( additionalResultsCount ) + " additional anime(s) were found with that name, this one was the best match." )

	# Respond with this embed
	return { "embed": embed }

# View personal member statistics
@chatCommands( category = "General", aliases = [ "stats" ] )
async def statistics( message, arguments, client ):

	# Fetch this member's statistics
	statistics = mysqlQuery( "SELECT Messages, Edits FROM MemberStatistics WHERE Member = LOWER( HEX( AES_ENCRYPT( '" + str( message.author.id ) + "', UNHEX( SHA2( '" + secrets.encryptionKeys.memberStatistics + "', 512 ) ) ) ) );" )[ 0 ]

	# Format each statistic
	messages = "{:,}".format( statistics[ 0 ] )
	edits = "{:,}".format( statistics[ 1 ] )

	# Respond with their statistics
	return { "content": ":bar_chart: You have sent a total of **" + messages + "** messages in this server & made **" + edits + "** edits to your own messages.\n*(Statistics from before 02/08/2020 07:01:05 UTC may not be 100% accurate)*" }

# View the top member statistics
@chatCommands( category = "General", aliases = [ "topstats", "leaderboard" ] )
async def topstatistics( message, arguments, client ):

	# Fetch the top 20 member statistics
	topStatistics = mysqlQuery( "SELECT AES_DECRYPT( UNHEX( Member ), UNHEX( SHA2( '" + secrets.encryptionKeys.memberStatistics + "', 512 ) ) ) AS Member, Messages, Edits FROM MemberStatistics ORDER BY Messages DESC LIMIT 20;" )

	# Create a blank embed
	embed = discord.Embed( title = "Top 20", description = "", color = settings.color )

	# Set a notice in the embed footer
	embed.set_footer( text = "Statistics from before 02/08/2020 07:01:05 UTC may not be 100% accurate." )

	# Loop through each top statistic
	for statistics in topStatistics:

		# The user's ID
		userID = int( statistics[ 0 ] )

		# Try to get the user from the client's cache
		user = client.get_user( userID )

		# Fetch basic user information via an API call if the user couldn't be found in the client's cache (they probably aren't on the guild)
		if user == None: user = await client.fetch_user( userID )

		# Format each statistic
		messages = "{:,}".format( statistics[ 1 ] )
		edits = "{:,}".format( statistics[ 2 ] )

		# Add it to the embed description
		embed.description += "• " + ( user.mention if user in message.guild.members else str( user ) ) + ": " + messages + " messages, " + edits + " edits.\n"

	# Respond with the embed
	return { "embed": embed }

# View the date & time you joined
@chatCommands( category = "General" )
async def joined( message, arguments, client ):

	# Fetch this date & time the member joined
	joinedAt = mysqlQuery( "SELECT FROM_UNIXTIME( AES_DECRYPT( Joined, UNHEX( SHA2( '" + secrets.encryptionKeys.members + "', 512 ) ) ) ) AS Joined FROM Members WHERE Member = AES_ENCRYPT( '" + str( message.author.id ) + "', UNHEX( SHA2( '" + secrets.encryptionKeys.members + "', 512 ) ) );" )[ 0 ][ 0 ]

	# Fetch the appropriate day suffix
	daySuffix = DAY_SUFFIXES.get( joinedAt.day, "th" )

	# Construct a formatting template using the day suffix
	template = "%A %-d" + daySuffix + " of %B %Y at %-H:%M:%S"

	# Get the pretty date & time
	joinedAtPretty = joinedAt.strftime( template )

	# Respond with a message
	return { "content": ":date: You joined this Discord server on **" + joinedAtPretty + "**.\n*(Information from before 08/08/2020 UTC may not be 100% accurate.)*" }

# Get the time in a specific timezone
@chatCommands( category = "General", aliases = [ "date" ] )
async def time( message, arguments, client ):

	# Default timezone is UTC
	timezoneQuery = "UTC"

	# Were there arguments provided?
	if len( arguments ) > 0:

		# Join the arguments together to make the new timezone
		timezoneQuery = " ".join( arguments )

	# Be safe!
	try:

		# Attempt to parse the timezone query
		timezone = pytz.timezone( timezoneQuery )

	# Catch unknown timezone errors
	except pytz.exceptions.UnknownTimeZoneError:

		# Respond with a message
		return { "content": ":grey_question: That doesn't appear to be a valid timezone name or identifier." }

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
	return { "content": ":calendar: " + timezonePretty }

# Get weather data for a location
@chatCommands( category = "General" )
async def weather( message, arguments, client ):

	# Are there no arguments provided?
	if len( arguments ) <= 0:

		# Friendly message
		return { "content": ":grey_exclamation: You must specify a location to fetch weather information for." }

	# Construct request URL
	locationQuery = "%20".join( arguments )
	apiURL = "https://api.openweathermap.org/data/2.5/weather?appid=" + secrets.apiKeys.openWeatherMap + "&units=metric&lang=en&q=" + locationQuery

	# Make the API request
	weatherRequest = requests.get( apiURL, headers = {
		"Accept": "application/json",
		"From": settings.email,
		"User-Agent": USER_AGENT_HEADER
	} )

	# Was a weather result not found?
	if weatherRequest.status_code == 404:

		# Friendly message
		return { "content": ":mag_right: I wasn't able to find weather data for a location with that name." }

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
	return { "embed": embed }

# Delete message sent in anonymous
@chatCommands( category = "General" )
async def delete( message, arguments, client ):

	# Is this not being used in a direct message?
	if message.guild != None:

		# Friendly message
		return { "content": ":exclamation: To protect your anonyminity, this command should only be used in Direct Messages with me." }

	# Was there no anime name provided?
	if len( arguments ) < 1:

		# Friendly message
		# TO-DO: delete after 10 seconds
		return { "content": ":grey_exclamation: You must specify the ID of the <#" + str( settings.channels.anonymous ) + "> message to delete." }

	# Fetch the guild
	guild = client.get_guild( settings.guild )

	# Fetch the anonymous channel
	anonymousChannel = guild.get_channel( settings.channels.anonymous )

	# Be safe!
	try:
		
		# Placeholder for the message ID
		messageID = None

		# Regex pattern for if they sent a message link as the argument
		messageLinkMatch = re.match( r"^https:\/\/discordapp\.com\/channels\/240167618575728644\/661694045600612352\/(\d{18})$", arguments[ 0 ] )

		# Was it a message link?
		if messageLinkMatch:

			# Set the message ID to the captured group
			messageID = messageLinkPattern.group( 1 )

		# It was not a message link
		else:

			# Set the message ID to the value of the entire argument
			messageID = arguments[ 0 ]

		# Fetch the specified message ID in the anonymous channel
		anonymousMessage = await anonymousChannel.fetch_message( int( messageID ) )

	# The message couldn't be found
	except discord.NotFound:

		# Friendly message
		# TO-DO: delete after 10 seconds
		return { "content": ":mag_right: I wasn't able to find a <#" + str( settings.channels.anonymous ) + "> message with that ID." }

	# The specified ID wasn't really an ID
	except ValueError:

		# Friendly message
		# TO-DO: delete after 10 seconds
		return { "content": ":grey_question: That doesn't appear to be a valid message ID." }

	# The message has been found
	else:

		# Calculate the message identifier and deletion token attempt
		messageIdentifier, deletionTokenAttempt = anonymousMessageHashes( anonymousMessage, message )

		# Try to see if a message with this identifier and deletion token exists
		existsResult = mysqlQuery( "SELECT EXISTS ( SELECT * FROM AnonMessages WHERE Message = '" + messageIdentifier + "' AND Token = '" + deletionTokenAttempt + "' );" )

		# Parse the results
		hasOwnership = bool( existsResult[ 0 ][ 0 ] )

		# Do they not own the message?
		if not hasOwnership:

			# Friendly message
			# TO-DO: delete after 10 seconds
			return { "content": ":no_entry_sign: The message has not been deleted because your ownership of it could not be verified.\n(Please note, <#" + str( settings.channels.anonymous ) + "> messages sent before the 22nd July 2020 cannot be deleted as no ownership information exists for them.)" }

			# Prevent further execution
			return

		# Delete the message from the anonymous channel
		await anonymousMessage.delete()

		# Remove the record from the database
		mysqlQuery( "DELETE FROM AnonMessages WHERE Message = '" + messageIdentifier + "' AND Token = '" + deletionTokenAttempt + "';" )

		# Friendly message
		# TO-DO: delete after 10 seconds
		return { "content": ":white_check_mark: The message has been successfully deleted." }

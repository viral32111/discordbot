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
# Import required modules
##############################################

import discord # Discord.py
import asyncio # Asyncronous code & events
import json # JSON parser
import requests # HTTP requests
import re # Regular expressions
import datetime, time # Date & time
import random # Randomisation
import os, sys # Host system (mostly file system interaction)
import traceback # Stacktraces
import hurry.filesize # Human-readable file sizes
import mysql.connector # MySQL databases
import hashlib # Cryptographic hashing
import xml.etree.ElementTree # XML parser for Rule #34 API responses
import mimetypes # Check mime/content type of media downloads
import shutil # Stream copy raw file objects
import pytz # Parsing timezone names/identifiers
import inspect # View the code of a function
import itertools # Chained iteration
import urllib.parse # Parsing URLs
import bs4 # Parsing & web scraping HTML
import difflib # For computing deltas
import operator # Extra sorting methods
import emoji # Resolving unicode emojis to text
import enum # Enumerations for custom classes
import mcstatus # Minecraft server status querying
import socket # Low level networking interface
import slashcommands # My Slash Commands API wrapper

# Console message
print( "Imported modules." )

##############################################
# Load configuration files
##############################################

# Create a global variable for holding the configuration
configuration = {}

# Loop through all files and directories in the config directory
for listing in os.listdir( "etc" ):

	# Store the path of this one
	path = os.path.join( "etc", listing )

	# Ignore anything that isn't a file
	if not os.path.isfile( path ): continue

	# Ignore anything that isn't a JSON file
	if not listing.endswith( ".json" ): continue

	# Open this configuration file as read only
	with open( path, "r" ) as configFile:

		# Store just the name of the file without the extension
		name = os.path.splitext( listing )[ 0 ]

		# Load this one into the global configuration
		configuration[ name ] = json.loads( configFile.read() )

# Console message
print( "Loaded configuration files." )

##############################################
# Initalise global variables
##############################################

# Cooldowns for anonymous relay
userCooldowns = {}

# The last sent messages for the anonymous relay
lastSentMessage = {}

# When the last dad joke was (default is 60 seconds in the past from now)
lastDadJoke = time.time() - 60

# A list to hold all of the created background tasks
backgroundTasks = []

# Console message
print( "Initalised global variables." )

##############################################
# Initalise global constants
##############################################

# User agent header for HTTP requests
USER_AGENT_HEADER = "Conspiracy AI/" + os.environ[ 'VERSION' ] + " (Discord Bot) Python/" + str( sys.version_info.major ) + "." + str( sys.version_info.minor ) + "." + str( sys.version_info.micro ) + " discord.py/" + discord.__version__ + " (github.com/viral32111/conspiracy-ai; " + configuration[ "general" ][ "email" ] + ")"

# Day suffixes for formatting timestamps
DAY_SUFFIXES = {
	1: "st",
	2: "nd",
	3: "rd",
	21: "st",
	22: "nd",
	23: "rd",
	31: "st"
}

# Template to allow for user pings only
ALLOW_USER_MENTIONS = discord.AllowedMentions(

	# Disable @everyone & @here pings
	everyone = False,

	# Allow user pings
	users = True,

	# Disable role pings
	roles = False

)

# Console message
print( "Initalised global constants." )
print( "User-Agent set to '" + USER_AGENT_HEADER + "'." )

##############################################
# Define helper functions
##############################################

# Check if a Discord object is valid
def isValid( obj ):

	# Messages
	if type( obj ) == discord.Message:
		if ( obj.author.id == client.user.id ) or ( not obj.guild ) or ( obj.type != discord.MessageType.default ):
			return False

	# Reactions
	elif type( obj ) == discord.Reaction:
		if ( obj.message.author.id == client.user.id ) or ( not obj.message.guild ):
			return False

	# Members
	elif type( obj ) == discord.Member or type( obj ) == discord.User:
		if obj.id == client.user.id:
			return False
	
	# Return true by default
	return True

# Convert a timestamp or datetime to a human readable format
def formatTimestamp( timestamp = datetime.datetime.utcnow() ):

	# Convert timestamps to datetime objects
	if type( timestamp ) is int:
		timestamp = datetime.datetime.fromtimestamp( timestamp )

	# Fetch the appropriate day suffix
	daySuffix = DAY_SUFFIXES.get( timestamp.day, "th" )

	# Construct a formatting template using the day suffix
	template = "%A %-d" + daySuffix + " of %B %Y at %-H:%M:%S UTC"

	# Return the formatted time using the above template
	return timestamp.strftime( template )

# Convert seconds to a human-readable format
def formatSeconds( secs ):

	# Calculate difference between now and the amount of seconds
	delta = datetime.timedelta( seconds = secs )

	# Try to match the delta against the regular expression
	match = re.match( r"^(?:(\d+) days?, )?(\d+):(\d+):(\d+)$", str( delta ) )

	# Return nothing if match failed
	if not match: return None

	# Extract each group from the matched groups tuple
	days, hours, minutes, seconds = match.groups()

	# Convert each group to integers (only convert days if it's valid)
	days, hours, minutes, seconds = ( int( days ) if days != None else 0 ), int( hours ), int( minutes ), int( seconds )

	# Construct the final sentence
	sentence = (
		( f"{days}d " if days > 0 else "" ) +
		( f"{hours}h " if hours > 0 else "" ) +
		( f"{minutes}m " if minutes > 0 else "" ) +
		( f"{seconds}s " if seconds > 0 else "" )
	) if secs > 0 else "0s"

	# Return that sentence
	return sentence

# Quickly and easily log an event
async def log( title, description, **kwargs ):

	# Fetch the logs channel
	logsChannel = client.get_channel( configuration[ "channels" ][ "logs" ] )

	guild = client.guilds[ 0 ]

	# Create an embed
	embed = discord.Embed( title = title, description = description, color = guild.me.top_role.color.value )

	# Set the footer to the current date & time
	embed.set_footer( text = formatTimestamp( datetime.datetime.utcnow() ) )

	# Set the jump link if it was provided
	jumpLink = kwargs.get( "jump", None )
	if jumpLink: embed.description += " [[Jump](" + jumpLink + ")]"

	# Set the image if it was provided
	imageLink = kwargs.get( "image", None )
	if imageLink: embed.set_image( url = imageLink )

	# Set the thumbnail if it was provided
	thumbnailLink = kwargs.get( "thumbnail", None )
	if thumbnailLink: embed.set_thumbnail( url = thumbnailLink )

	# Send the embed to the logs channel
	await logsChannel.send( embed = embed )

# Get the message identifier and deletion token for an anonymous message send/delete
def anonymousMessageHashes( anonymousMessage, authorID ):

	# Store the secret sauce
	secretSauce = os.environ[ "ANONYMOUS_SALT" ]

	# The message identifier, soon to be hashed!
	messageIdentifier = str( anonymousMessage.id ).encode( "utf-8" )

	# The deletion token, soon to be hashed!
	deletionToken = ( str( time.mktime( anonymousMessage.created_at.timetuple() ) ) + str( authorID ) ).encode( "utf-8" )

	# Iterate for the length of the secret sauce
	for iteration in range( 1, len( secretSauce ) ):

		# Hash the message identifier
		messageIdentifier = hashlib.sha3_512( ( secretSauce + str( messageIdentifier ) ).encode( "utf-8" ) ).hexdigest()

		# Hash the deletion token
		deletionToken = hashlib.sha3_512( ( secretSauce + str( deletionToken ) ).encode( "utf-8" ) ).hexdigest()

	# Shorten the message identifier to make it look like another hash algorithm
	messageIdentifier = messageIdentifier[ :24 ]

	# Shorten the deletion token to make it look like another hash algorithm
	deletionToken = deletionToken[ :64 ]

	# Return them both
	return messageIdentifier, deletionToken

# Run a MySQL query on the database and return the results
def mysqlQuery( sql ):

	# Connect to the database
	connection = mysql.connector.connect(
		host = configuration[ "database" ][ "host" ],
		port = configuration[ "database" ][ "port" ],
		user = os.environ[ "DATABASE_USERNAME" ],
		password = os.environ[ "DATABASE_PASSWORD" ],
		database = configuration[ "database" ][ "name" ]
	)
	
	# Placeholder for the final results
	results = None

	# Be safe!
	try:

		# Fetch the database cursor
		cursor = connection.cursor()

		# Run the query
		cursor.execute( sql )

		# Is the query expected to return data?
		if sql.startswith( "SELECT" ):

			# Store the results
			results = cursor.fetchall()

		else:

			# Commit changes
			connection.commit()

	# Catch all errors
	except:

		# Print a stacktrace
		print( traceback.format_exc() )

		# Rollback changes
		connection.rollback()

		# Set results to nothing
		results = None

	# Do this even if there was an error
	finally:

		# Close the database cursor
		cursor.close()

		# Close the connection
		connection.close()

	# Return the results
	return results

# Get the direct URL from a Tenor vanity URL
def extractDirectTenorURL( vanityURL ):

	# Request the vanity URL page
	vanity = requests.get( vanityURL, headers = {
		"Accept": "text/html, */*",
		"User-Agent": USER_AGENT_HEADER,
		"From": configuration[ "general" ][ "email" ]
	} )

	# Create parsing soup from the received HTML
	soup = bs4.BeautifulSoup( vanity.text, features = "html.parser" )

	# Return the found image source URL in html > head > link > image_src
	return soup.find( "link", { "class": "dynamic", "rel": "image_src" } )[ "href" ]

# Download media over HTTP and save it to disk
def downloadWebMedia( originalURL, subDirectory = "downloads" ):

	# Set the directory of where to save the file to
	directory = "/tmp/" + subDirectory # "/volume/downloads" if keepForever else "/tmp/downloads"

	# Create the directory if it doesn't exist
	os.makedirs( directory, 0o700, exist_ok = True )

	# Get the current date & time in UTC
	rightNow = datetime.datetime.utcnow()

	# Is this a vanity Tenor URL?
	if re.match( r"^https?:\/\/(www\.)?tenor\.com\/view\/.+", originalURL ):

		# Set the original URL to the extracted direct URL
		originalURL = extractDirectTenorURL( originalURL )

	# Request just the headers of the remote web file
	head = requests.head( originalURL, headers = {
		"Accept": "image/*, video/*, audio/*, */*",
		"User-Agent": USER_AGENT_HEADER,
		"From": configuration[ "general" ][ "email" ]
	} )

	# Store the headers except with lowercase field names
	headers = { key.lower(): value for key, value in head.headers.items() }

	# Return nothing if there is no content from the request
	if "content-type" not in headers or "content-length" not in headers: return None

	# Return nothing if the content is over 100MiB
	if int( headers[ "content-length" ] ) > 104857600: return None

	# Return nothing if the content isn't an image, video or audio file
	if not re.match( r"^image\/(.+)|^video\/(.+)|^audio\/(.+)", head.headers[ "content-type" ] ): return None

	# Parse the original URL
	parsedURL = urllib.parse.urlparse( originalURL )

	# Get the URL's file extension (this includes the .)
	extension = os.path.splitext( parsedURL.path )[ 1 ]

	# If the URL has no file extension then guess it based on the returned mime-type (this includes the .)
	if extension == "": extension = mimetypes.guess_extension( headers[ "content-type" ] )

	# Force the file extension to lower-case
	extension = extension.lower()

	# Create a hash of the URL to use as the local file's name
	hashedURL = hashlib.sha256( originalURL.encode( "utf-8" ) ).hexdigest()

	# The local file's full path
	path = directory + "/" + hashedURL + extension

	# Does the local file already exist and is the last modified header present?
	if os.path.isfile( path ) and "last-modified" in headers:

		# Parse the value of the header
		lastModified = datetime.datetime.strptime( headers[ "last-modified" ], "%a, %d %b %Y %H:%M:%S GMT" )

		# Return the local path if the file hasn't been modified since it was last saved - no need to redownload (hopefully)
		if lastModified < datetime.datetime.utcfromtimestamp( os.path.getmtime( path ) ): return path

	# Request the full content to stream-download it
	get = requests.get( originalURL, stream = True, headers = {
		"Accept": "image/*, video/*, audio/*, */*",
		"User-Agent": USER_AGENT_HEADER,
		"From": configuration[ "general" ][ "email" ]
	} )

	# Open the local file in binary write mode
	with open( path, "wb" ) as handle:

		# Write the raw stream to the file 
		shutil.copyfileobj( get.raw, handle )

	# Return the final path
	return path

# Get the checksum a local file on disk
def fileChecksum( path, algorithm = hashlib.sha256 ):

	# Create the hasher
	hasher = algorithm()

	# Open the file in binary reading mode
	with open( path, "rb" ) as handle:

		# Loop forever
		while True:

			# Read a chunk of data from the file
			data = handle.read( 65535 )

			# Exit loop if there is no data left
			if len( data ) < 1: break

			# Update the hash
			hasher.update( data )

		# Get the final hex checksum
		checksum = hasher.hexdigest()

	# Return the final hex checksum
	return checksum

# Check if a link is a repost
def isRepost( url ):

	# Download the media file at the URL
	path = downloadWebMedia( url, "reposts" )

	# Return nothing if the file wasn't downloaded - this should mean the file wasn't an image/video/audio file, or was over 100 MiB
	if path == None: return None

	# Get the checksum of the file contents
	checksum = fileChecksum( path )

	# Get the location & repost count for this content from the database
	results = mysqlQuery( "SELECT Channel, Message, Count FROM RepostHistory WHERE Checksum = '" + checksum + "';" )

	# Return false & the checksum if no data was returned
	if len( results ) < 1: return [ False, checksum ]

	# Convert the tuple to a list
	information = list( results[ 0 ] )

	# Add the checksum to the list
	information.append( checksum )

	# Return the repost information
	return information

# Should logs happen for this message?
def shouldLog( message ):

	# Return false if this a direct message
	if message.guild == None: return False

	# Return false if this message is from a bot
	if message.author.bot: return False

	# Return true otherwise
	return True

# Convert a string to just ASCII characters
def ascii( string ):

	# Strip all non-ASCII characters and return it
	return string.encode( "ascii", "ignore" ).decode( "ascii" ).strip()

# Convert a string to just UTF-8 characters
def utf8( string ):

	# Strip all non-UTF-8 characters and return it
	return string.encode( "utf-8", "ignore" ).decode( "utf-8" ).strip()

# Console message
print( "Defined helper functions." )

##############################################
# Define Slash Commands
##############################################

# Import each chat command file
from commands import minecraft
from commands import hentai
from commands import fun
from commands import subscriptions
from commands import links
from commands import anime
from commands import moderation
from commands import administration
from commands import music
from commands import general

# Console message
print( "Defined slash commands." )

##############################################
# Initalise the client
##############################################

# Create the client
client = discord.Client(

	# Set initial status to idle to indicate not ready yet
	status = discord.Status.dnd if len( sys.argv ) > 1 else discord.Status.idle,

	# Set the initial activity to loading
	activity = discord.Game( "Loading..." ),

	# Max messages to cache internally
	max_messages = 10000,

	# Cache members that are offline
	chunk_guilds_at_startup = True,

	# Set the default allowed mentions for each message sent by the bot
	allowed_mentions = discord.AllowedMentions(

		# Disable @everyone & @here pings
		everyone = False,

		# Disable user pings
		users = False,

		# Disable role pings
		roles = False

	),

	# Set the session intents to all available intents
	intents = discord.Intents.all()

)

##############################################
# Define background tasks
##############################################

# Automatically randomise the client's activity
async def chooseRandomActivity():

	# Be safe!
	try:

		# Loop forever
		while not client.is_closed():

			# Choose a random activity
			activity = random.choice( configuration[ "activities" ] )

			# Set the default activity type
			activityType = discord.ActivityType.playing

			# Set the default activity text
			activityText = activity[ 8: ]

			# Is it watching?
			if activity.startswith( "Watching " ):

				# Set the activity type to watching
				activityType = discord.ActivityType.watching

				# Set the activity text
				activityText = activity[ 9: ]

			# Is it listening to?
			elif activity.startswith( "Listening to " ):

				# Set the activity type to watching
				activityType = discord.ActivityType.listening

				# Set the activity text
				activityText = activity[ 13: ]

			# Update the client's presence
			await client.change_presence(

				# Use a specific status
				status = discord.Status.dnd if len( sys.argv ) > 1 else discord.Status.online,

				# Use the randomly chosen activity
				activity = discord.Activity(
					type = activityType,
					name = activityText,
				)

			)

			# Run this again in 5 minutes
			await asyncio.sleep( 300 )

	# Catch task cancellation calls
	except asyncio.CancelledError:

		# Console message
		print( "Cancelled random activity chooser background task." )

# Update the Minecraft category name with the server's status
async def updateMinecraftCategoryStatus():
	try:
		category = client.get_channel( 805818251728388156 )
		server = mcstatus.MinecraftServer( "viral32111.com", 25565 )
		while not client.is_closed():
			text = "Unknown"
			try:
				status = await server.async_status()
			except socket.timeout:
				text = "Offline"
			else:
				text = ( f"{status.players.online} online" if status.players.online > 0 else "Empty" )
			await category.edit( name = f"🧱 Minecraft ({ text })", reason = "Update Minecraft category server status." )
			await asyncio.sleep( 120 )
	except asyncio.CancelledError:
		print( "Cancelled update Minecraft category status background task." )

# Console message
print( "Defined background tasks." )

##############################################
# Define callbacks
##############################################

# Runs when the client successfully connects
async def on_connect():

	# Console message
	print( "Connected to Discord." )

# Runs when the client resumes a previous connection
async def on_resumed():

	# Bring some global variables into this scope
	global backgroundTasks

	# Launch background tasks - keep this the same as on_ready()!
	backgroundTasks.append( client.loop.create_task( chooseRandomActivity() ) )
	backgroundTasks.append( client.loop.create_task( updateMinecraftCategoryStatus() ) )
	print( "Created background tasks." )

	# Console message
	print( "Resumed connection to Discord." )

# Runs when the client disconnects
async def on_disconnect():

	# Cancel all background tasks
	for backgroundTask in backgroundTasks: backgroundTask.cancel()

	# Remove all background tasks from the list
	backgroundTasks.clear()

	# Console message
	print( "Disconnected from Discord." )

# Runs when a message is received
async def on_message( message ):

	# Bring globals into this scope
	global lastDadJoke, userCooldowns, lastSentMessage

	# Ignore messages from ourselves or other bots
	if message.author.id == client.user.id or message.author.bot: return

	# Ignore system messages (member joined, nitro boosted, etc)
	if message.type != discord.MessageType.default: return

	# Try to get the member from the guild members directly
	guildMember = discord.utils.get( client.guilds[ 0 ].members, id = message.author.id )

	# Ignore direct messages if the author isn't in the discord server
	if message.guild == None and guildMember == None:

		# Friendly message
		await message.author.dm_channel.send( ":exclamation: You must be a member of the Conspiracy Servers Discord to use me.\nJoin here: https://viral32111.com/discord", delete_after = 60 )

		# Prevent further execution
		return

	# Is the bot pinged at all in this message?
	if client.user.mentioned_in( message ):

		# Appreciation reaction
		await message.add_reaction( random.choice( [ "❤️", "💟", "❣️", "😍", "♥️", "🖤", "💙", "🤎", "💚", "💝", "💖", "💕", "🤍", "💛", "🧡", "💜", "💞", "🥰", "💓", "😘", "💗", "🤟", "💘" ] ) )

	# Escape markdown and remove pings
	safeContent = discord.utils.escape_markdown( message.clean_content )

	# Extract all links from the message's content
	inlineURLs = re.findall( r"(https?://[^\s]+)", message.content )

	# Get all attachment links from attachments with the message
	attachmentURLs = [ attachment.url for attachment in message.attachments ]

	# Store the current unix timestamp for later use
	unixTimestampNow = time.time()

	# Is this message sent from a guild?
	if message.guild != None:

		# Console message
		print( "(" + ascii( message.channel.category.name ) + " -> #" + message.channel.name + ") " + str( message.author ) + " (" + message.author.display_name + "): " + message.content + ( "\n\t".join( attachmentURLs ) if len( attachmentURLs ) > 0 else "" ) )

		# Create or increment the message sent statistic for this member
		mysqlQuery( "INSERT INTO MemberStatistics ( Member ) VALUES ( LOWER( HEX( AES_ENCRYPT( '" + str( message.author.id ) + "', UNHEX( SHA2( '" + os.environ[ "ENCRYPTION_STATISTICS" ] + "', 512 ) ) ) ) ) ) ON DUPLICATE KEY UPDATE Messages = Messages + 1;" )

		# Is this the memes channel?
		if message.channel.id == configuration[ "channels" ][ "memes" ]:

			# Loop through all of those inline links and attachment links
			for url in itertools.chain( attachmentURLs, inlineURLs ):

				# Get any repost information
				repostInformation = isRepost( url )

				# Skip if the information is nothing - this means the link is not an image/video/audio file, or is over 100 MiB
				if repostInformation == None: continue

				# Is this not a repost?
				if repostInformation[ 0 ] == False:

					# Get the location information using a regular expression
					location = re.search( r"(\d+)/(\d+)$", message.jump_url )

					# Add repost information to the database
					mysqlQuery( "INSERT INTO RepostHistory ( Checksum, Channel, Message ) VALUES ( '" + repostInformation[ 1 ] + "', " + location.group( 1 ) + ", " + location.group( 2 ) + " );" )

					# Console message
					print( "Adding original message attachment with checksum '" + repostInformation[ 1 ] + "' to the repost history database for the first time." )

				# It is a repost
				else:

					# Be safe!
					try:

						# Get the channel it was sent in
						channel = client.get_channel( repostInformation[ 0 ] )

						# Raise not found if channel is nothing
						if channel == None: raise discord.NotFound()

						# Fetch the original message from that channel
						originalMessage = await channel.fetch_message( repostInformation[ 1 ] )

					# The original message does not exist
					except discord.NotFound:

						# Get the location information using a regular expression
						location = re.search( r"(\d+)/(\d+)$", message.jump_url )

						# Update the record in the database to have this message as the first one
						mysqlQuery( "UPDATE RepostHistory SET Channel = " + location.group( 1 ) + ", Message = " + location.group( 2 ) + ", Count = 1 WHERE Checksum = '" + repostInformation[ 3 ] + "';" )

					# The original message exists
					else:

						# Is this not the original author reposting their own content?
						if originalMessage.author.id != message.author.id:

							# Update the count in the database
							mysqlQuery( "UPDATE RepostHistory SET Count = Count + 1 WHERE Checksum = '" + repostInformation[ 3 ] + "';" )

							# Console message
							print( "Incrementing repost count for message attachment with checksum '" + repostInformation[ 3 ] + "' in the repost history database." )

							# Inform them via reply
							await message.reply( ":recycle: This is a repost, I've seen it **" + str( repostInformation[ 2 ] ) + "** time" + ( "s" if repostInformation[ 2 ] > 1 else "" ) + " before!\n*(Original: <https://discord.com/channels/" + str( client.guilds[ 0 ].id ) + "/" + str( repostInformation[ 0 ] ) + "/" + str( repostInformation[ 1 ] ) + ">)*", mention_author = False )

		# Does the message start with "Im " and has it been 15 seconds since the last one?
		if message.content.startswith( "Im " ) and ( lastDadJoke + 15 ) < unixTimestampNow:

			# Send dadbot response
			await message.channel.send( "Hi " + message.clean_content[ 3: ] + ", I'm dad!" )

			# Set the last dad joke date & time
			lastDadJoke = unixTimestampNow

	# This message was sent over direct messages
	else:

		anonymousChannel = client.guilds[ 0 ].get_channel( configuration[ "channels" ][ "anonymous" ] )
		anonymousChannelWebhooks = await anonymousChannel.webhooks()
		anonymousWebhook = anonymousChannelWebhooks[ 0 ]

		lurkerRole = discord.utils.get(client.guilds[ 0 ].roles,id=807559722127458304)
		timeoutRole=discord.utils.get(client.guilds[ 0 ].roles,id=539160858341933056)

		# Disallow lurkers
		if(lurkerRole in guildMember.roles):
			await message.author.dm_channel.send( f"Sorry, to use the anonymous chat system, you cannot be a lurker in the Discord server.", delete_after = 10 )
			return

		# Disallow members in timeout
		if (timeoutRole in guildMember.roles):
			await message.author.dm_channel.send( "Sorry, you've been temporarily restricted from using the anonymous chat, because you're in timeout.", delete_after = 10 )
			return

		# Don't allow them to send the same message twice
		if(message.clean_content!="" and str(message.author.id)in lastSentMessage):
			if(lastSentMessage[str(message.author.id)]==message.clean_content):
				await message.author.dm_channel.send( "Please do not send the same message twice.", delete_after = 10 )
				return

		# Wait 5 seconds before sending another message
		if(str(message.author.id)in userCooldowns):
			if(time.time()-userCooldowns[str(message.author.id)]<=5):
				await message.author.dm_channel.send( "Please wait at least 5 seconds before sending another message.", delete_after = 10 )
				return

		# Update cooldown and last message sent
		userCooldowns[str(message.author.id)]=time.time()
		if(message.clean_content!=""):lastSentMessage[str(message.author.id)]=message.clean_content

		# Pick random username and avatar
		username = random.choice( configuration[ "names" ] )
		randomAvatarHash = random.choice( [
			"1cbd08c76f8af6dddce02c5138971129",
			"0e291f67c9274a1abdddeb3fd919cbaa",
			"dd4dbc0016779df1378e7812eabaa04d",
			"322c936a8c8be1b803cd94861bdfa868",
			"6debd47ed13483642cf09e832ed0bc1b"
		] )
		avatar = f"https://discordapp.com/assets/{ randomAvatarHash }.png"

		# A placeholder list for all the discord file objects
		files = []

		# Loop through all attachments that the user uploads
		for attachment in message.attachments:

			# Download the attachment
			path = downloadWebMedia( attachment.url, "anonymous" )

			# Skip if the attachment wasn't downloaded
			if path == None: continue

			# Get the file extension
			_, extension = os.path.splitext( path )

			# Create an identical discord file object and append it to the files list
			files.append( discord.File( path, filename = "unknown" + extension, spoiler = attachment.is_spoiler() ) )

		# What to do after sending a message
		async def afterSentAnonMessage( anonMessage, directMessage ):

			# Calculate the message identifier and real deletion token
			messageIdentifier, deletionToken = anonymousMessageHashes( anonMessage, directMessage.author.id )

			# Add this message into the database
			insertResult = mysqlQuery( "INSERT INTO AnonMessages ( Message, Token ) VALUES ( '" + messageIdentifier + "', '" + deletionToken + "' );" )

		# Send to the anonymous channel
		try:
			if(len(files)==1):
				anonMessage = await anonymousWebhook.send(message.clean_content,file=files[0],username=username,avatar_url=avatar, wait = True )
				await afterSentAnonMessage( anonMessage, message )
			elif(len(files)>1):
				anonMessage = await anonymousWebhook.send(message.clean_content,files=files,username=username,avatar_url=avatar, wait = True )
				await message.author.dm_channel.send("You seem to have uploaded multiple files in a single message, while this can be relayed it is prone to issues by sometimes not relaying all of the uploaded files at once and instead only relaying the last uploaded file. To avoid this, upload all your files in seperate messages.", delete_after = 10 )
				await afterSentAnonMessage( anonMessage, message )
			elif(message.clean_content!=""):
				anonMessage = await anonymousWebhook.send(message.clean_content,username=username,avatar_url=avatar, wait = True )
				await afterSentAnonMessage( anonMessage, message )
		except discord.errors.HTTPException as errorMessage:
			if(errorMessage.code==40005):
				await message.author.dm_channel.send("Sorry, I wasn't able to relay that message because it was too large. If you uploaded multiple files in a single message, try uploading them in seperate messages.", delete_after = 10 )
				pass

# Runs when a member joins the server
async def on_member_join( member ):

	# Is this member a bot?
	if member.bot:

		# Log this bot add event
		await log( "Bot added", member.mention + " has been added to the server.", thumbnail = member.avatar_url )

	# They are a normal user
	else:

		# Fetch the join/leave messages channel
		welcomeChannel = client.get_channel( configuration[ "channels" ][ "welcome" ] )

		# Log this member join event
		await log( "Member joined", member.mention + " joined the server.", thumbnail = member.avatar_url )

		# Query the date & time that the member joined from the database
		results = mysqlQuery( "SELECT FROM_UNIXTIME( AES_DECRYPT( Joined, UNHEX( SHA2( '" + os.environ[ "ENCRYPTION_MEMBERS" ] + "', 512 ) ) ) ) AS Joined, AES_DECRYPT( Steam, UNHEX( SHA2( '" + os.environ[ "ENCRYPTION_MEMBERS" ] + "', 512 ) ) ) AS Steam FROM Members WHERE Member = AES_ENCRYPT( '" + str( member.id ) + "', UNHEX( SHA2( '" + os.environ[ "ENCRYPTION_MEMBERS" ] + "', 512 ) ) );" )

		# Have they been in the server before? (we got results from the database)
		if len( results ) > 0:

			# Set their year role to whatever joined at date & time was in the database
			yearJoined = results[ 0 ][ 0 ].year

			# Do they have their Steam account linked?
			if results[ 0 ][ 1 ]:

				# Fetch the Steam Linked role
				membersRole = member.guild.get_role( configuration[ "roles" ][ "steamlink" ] )

				# Give the member that year role and the Steam Linked role
				await member.add_roles( membersRole, reason = "Member has their Steam account linked." )

			# Send a welcome back message to the join/leave messages channel
			await welcomeChannel.send( ":wave_tone1: Welcome back " + member.mention + ", it's great to see you here again!", allowed_mentions = ALLOW_USER_MENTIONS )

		# This is their first time joining (we didn't get any results from the database)
		else:

			# Add the member to the database
			mysqlQuery( "INSERT INTO Members ( Member, Joined ) VALUES ( AES_ENCRYPT( '" + str( member.id ) + "', UNHEX( SHA2( '" + os.environ[ "ENCRYPTION_MEMBERS" ] + "', 512 ) ) ), AES_ENCRYPT( UNIX_TIMESTAMP( STR_TO_DATE( '" + member.joined_at.strftime( "%Y-%m-%d %H:%M:%S" ) + "', '%Y-%m-%d %H:%i:%S' ) ), UNHEX( SHA2( '" + os.environ[ "ENCRYPTION_MEMBERS" ] + "', 512 ) ) ) );" )

			# Set their year role to when they joined (which should always be right now, unless Discord is taking a shit)
			yearJoined = member.joined_at.year

			# Send a first welcome message to the join/leave messages channel
			await welcomeChannel.send( ":wave_tone1: Welcome " + member.mention + " to the community!", allowed_mentions = ALLOW_USER_MENTIONS )

		# Fetch the role for the year we just set above (WARNING: THIS WILL BREAK ON NEW YEAR UNLESS A ROLE FOR THAT YEAR IS MANUALLY CREATED)
		yearRole = discord.utils.get( member.guild.roles, name = str( yearJoined ) )

		# Give the member that year role
		await member.add_roles( yearRole, reason = "Member joined the server." )

# Runs when a member leaves
async def on_member_remove(member):
	await client.wait_until_ready()

	# Fetch the join/leave messages channel
	welcomeChannel = client.get_channel( configuration[ "channels" ][ "welcome" ] )

	moderator, reason, event = None, None, 0
	after = datetime.datetime.now()-datetime.timedelta(seconds=5)

	# -- This currently doesn't work and only displays the user as leaving.
	# Something todo with the 'entry.created_at > after' code, need to find a way to check if one datetime object is less than another. (the time is before!)
	async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
		if (entry.created_at > after) and (entry.target.id == member.id):
			moderator, event, reason = entry.user, 1, (entry.reason or None)
			break

	if (moderator == None): # If it didn't find them in the kicks, it surley was a ban, right?
		async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
			if (entry.created_at > after) and (entry.target.id == member.id):
				moderator, event, reason = entry.user, 2, (entry.reason or None)
				break

	if (event == 1):
		await welcomeChannel.send(f":bangbang: {member} was kicked by {moderator.mention}" + (f" for {reason}" if (reason) else "") + ".")
		await log("Member kicked", f"{member} was kicked by {moderator.mention}" + (f" for `{reason}`" if (reason) else "") + ".", thumbnail=member.avatar_url)
	elif (event == 2):
		await welcomeChannel.send(f":bangbang: {member} was banned by {moderator.mention}" + (f" for {reason}" if (reason) else "") + ".")
		await log("Member banned", f"{member} was banned by {moderator.mention}" + (f" for `{reason}`" if (reason) else "") + ".", thumbnail=member.avatar_url)
	else:
		await welcomeChannel.send(f":man_walking_tone1: {member} left the server.")
		await log("Member left", f"{member} left the server.", thumbnail=member.avatar_url)

# Runs when a message is deleted
async def on_message_delete( message ):

	# Do not continue if this is a direct message
	if not message.guild: return

	# Do not continue if this was one of our messages
	if message.author.id == client.user.id: return

	# Do not continue if this is not a regular message
	if message.type != discord.MessageType.default: return

	# Set the member that deleted this message to the original message author by default
	deleter = message.author

	# Wait a few seconds for the audit log to be populated
	await asyncio.sleep( 2 )

	# Fetch the most recent audit log entry for a message deletion event that happened before 5 seconds in the future and after 5 seconds ago
	async for entry in message.guild.audit_logs( limit = 1, action = discord.AuditLogAction.message_delete, before = datetime.datetime.utcnow() + datetime.timedelta( seconds = 5 ), after = datetime.datetime.utcnow() - datetime.timedelta( seconds = 5 ) ):

		# Is this entry for this message deletion event? (best guess)
		if entry.target.id == message.author.id and entry.extra.channel.id == message.channel.id and message.created_at <= entry.created_at:

			# Set the member that deleted this message to the user in the entry
			deleter = entry.user

	# Was this message deleted by the original message author?
	if deleter.id == message.author.id:

		# Increment the message deletion statistic for the original author
		mysqlQuery( "UPDATE MemberStatistics SET Deletions = Deletions + 1 WHERE Member = LOWER( HEX( AES_ENCRYPT( '" + str( message.author.id ) + "', UNHEX( SHA2( '" + os.environ[ "ENCRYPTION_STATISTICS" ] + "', 512 ) ) ) ) );" )

	# Prevent further execution if this event should not be logged
	if not shouldLog( message ): return

	# Does this message include attachments?
	if len( message.attachments ) > 0:

		# Loop through each attachment in the message
		for attachment in message.attachments:

			# If the attachment is an image or video
			if attachment.width and attachment.height:

				# Log this deletion
				await log( "Image deleted", f"Image [{ attachment.filename } ({ attachment.width }x{ attachment.height }) ({ hurry.filesize.size( attachment.size, system = hurry.filesize.alternative) })]({ attachment.proxy_url }) uploaded by { message.author.mention } in { message.channel.mention } was deleted by { deleter.mention }.", image = attachment.proxy_url )
			
			# The attachment is not an image or video
			else:

				# Log this deletion
				await log( "Upload deleted", f"Upload [{ attachment.filename } ({ hurry.filesize.size( attachment.size, system = hurry.filesize.alternative ) })]({ attachment.url }) uploaded by { message.author.mention } in { message.channel.mention } was deleted by { deleter.mention }." )

	# If the message has content
	if message.content != "":

		# Log this deletion
		await log( "Message deleted", f"`{ message.content }` sent by { message.author.mention } in { message.channel.mention } was deleted by { deleter.mention }." )

# Runs when a message is edited
async def on_message_edit(originalMessage, editedMessage):

	# Don't run if this is a Direct Message
	if originalMessage.guild == None: return

	if (not isValid(originalMessage)) or (originalMessage.clean_content == editedMessage.clean_content): return

	# Increment the message edit statistic for this member
	mysqlQuery( "UPDATE MemberStatistics SET Edits = Edits + 1 WHERE Member = LOWER( HEX( AES_ENCRYPT( '" + str( originalMessage.author.id ) + "', UNHEX( SHA2( '" + os.environ[ "ENCRYPTION_STATISTICS" ] + "', 512 ) ) ) ) );" )

	# Prevent further execution if this event shouldn't be logged
	if not shouldLog( originalMessage ): return

	if (originalMessage.clean_content == "") and (editedMessage.clean_content != ""):
		await log("Message edited", f"{originalMessage.author.mention} added `{editedMessage.clean_content}` to their message in {originalMessage.channel.mention}.", jump=editedMessage.jump_url)
	else:
		await log("Message edited", f"{originalMessage.author.mention} changed their message from `{originalMessage.clean_content}` to `{editedMessage.clean_content}` in {originalMessage.channel.mention}.", jump=editedMessage.jump_url)

# Runs when a reaction is added to a message
async def on_reaction_add(reaction, user):

	# Don't run if this is a Direct Message
	if reaction.message.guild == None: return

	# Console message
	print(f"{user} added {reaction.emoji} to {reaction.message.content}.")

	# Duplicate the reaction
	#await reaction.message.add_reaction(reaction)

# Runs when a reaction is removed from a message
async def on_reaction_remove(reaction, user):

	# Don't run if this is a Direct Message
	if reaction.message.guild == None: return

	# Console message
	print(f"{user} removed {reaction.emoji} from {reaction.message.content}.")

# Runs when a member's voice state changes
async def on_voice_state_update( member, before, after ):

	# Ignore bots
	if member.bot: return

	# Just give everyone music DJ for now
	dj_role = member.guild.get_role( 784532835348381776 )
	await member.add_roles( dj_role )
	return

	# Has the member joined the Music voice channel?
	if after.channel != None and after.channel.id == 257480146762596352:

		# Get the members in the voice channel, excluding bots
		membersNoBots = [ member for member in after.channel.members if member.bot == False ]

		# Are they the first member to join?
		if len( membersNoBots ) == 1:

			# Get the DJ role
			dj_role = member.guild.get_role( 784532835348381776 )

			# Get the #commands channel
			commands_channel = client.get_channel( 241602380569772044 )

			# Give them the DJ role
			await member.add_roles( dj_role, reason = "Member is now the DJ." )

			# Send a message
			await commands_channel.send( member.mention + " is now the " + dj_role.mention + "." )

	# Has the member left the Music voice channel?
	elif before.channel != None and before.channel.id == 257480146762596352:

		# Loop through their roles
		for role in member.roles:

			# Is this the DJ role?
			if role.id == 784532835348381776:

				# Get the DJ role
				dj_role = member.guild.get_role( 784532835348381776 )

				# Get the #commands channel
				commands_channel = client.get_channel( 241602380569772044 )

				# Remove the role from them
				await member.remove_roles( dj_role, reason = "Member is no longer the DJ." )

				# Send a message
				await commands_channel.send( member.mention + " is no longer the " + dj_role.mention + "." )

				# Stop the loop
				break

# Runs when any payload is received from the gateway (but we're using it for interactions)
async def on_socket_response( payload ):
	command = await slashcommands.run( payload, client )
	if command:
		now = datetime.datetime.now().strftime( "%d-%m-%Y %H:%M:%S.%f" )
		channel = client.get_channel( command.channelID )
		print( f"[{ now }] { command.user.username }#{ command.user.discriminator } ({ command.user.id }) used /{ command.data.name } ({ command.data.id }) in #{ channel.name } ({ channel.id }) with arguments '{ command.arguments }'." )

		guild = client.guilds[ 0 ]

		logEmbed = discord.Embed(
			title = "Slash Command Used",
			color = guild.me.top_role.color.value,
			timestamp = datetime.datetime.utcnow()
		)

		logEmbed.add_field(
			name = "__Member__",
			value = f"<@{ command.user.id }>\n`{ command.user.id }`",
			inline = True
		)

		logEmbed.add_field(
			name = "__Command__",
			value = f"`/{ command.data.name }`\n`{ command.data.id }`",
			inline = True
		)

		logEmbed.add_field(
			name = "__Location__",
			value = f"<#{ channel.id }>\n`{ channel.id }`",
			inline = True
		)

		logEmbed.add_field(
			name = "__Arguments__",
			value = f"```json\n{ command.arguments }\n```",
			inline = False
		)

		logEmbed.set_footer(
			text = formatTimestamp( datetime.datetime.utcnow() )
		)

		logsChannel = client.get_channel( 576904701304635405 )
		await logsChannel.send( embed = logEmbed )

# Runs when the client is ready
async def on_ready():

	# Bring some global variables into this scope
	global backgroundTasks

	# Register the rest of the callbacks
	client.event( on_message )
	client.event( on_message_edit )
	client.event( on_message_delete )
	client.event( on_member_join )
	client.event( on_member_remove )
	client.event( on_reaction_add )
	client.event( on_reaction_remove )
	client.event( on_voice_state_update )
	print( "Registered callbacks." )

	# Launch background tasks - keep this the same as on_ready()!
	backgroundTasks.append( client.loop.create_task( chooseRandomActivity() ) )
	backgroundTasks.append( client.loop.create_task( updateMinecraftCategoryStatus() ) )
	print( "Created background tasks." )

	# Console message
	print( "Ready." )

# Register a few initial callbacks
client.event( on_connect )
client.event( on_resumed )
client.event( on_disconnect )
client.event( on_ready )
client.event( on_socket_response )

try:
	print( "Logging in..." )
	client.loop.run_until_complete( client.login( os.environ[ "DISCORD_TOKEN" ] ) )

	print( "Connecting..." )
	client.loop.run_until_complete( client.connect() )
except KeyboardInterrupt:
	if not client.is_ready():
		print( "Waiting until client is ready..." )
		client.loop.run_until_complete( client.wait_until_ready() )

	print( "Closing..." )
	for backgroundTask in backgroundTasks: backgroundTask.cancel()
	client.loop.run_until_complete( client.change_presence( status = discord.Status.offline ) )
	client.loop.run_until_complete( client.close() )
finally:
	client.loop.close()
	print( "Closed." )

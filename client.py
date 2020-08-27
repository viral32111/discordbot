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

# Emojis for chat command feedback:
# :exclamation:			Incorrect channel for command (NSFW cmd not being used in channel marked as NSFW, etc)
# :grey_question:		Unknown / Invalid arguments
# :grey_exclamation:	Not enough arguments given / Incorrect command usage
# :interrobang:			Internal error / Invalid API response
# :no_entry_sign:		Not enough permissions / Cannot be used by you
# :mag_right:			Search error (mainly for APIs)
# :wrench:				Command is in development
# :white_check_mark:	Successful action
# :information_source:	Information / Help / Assistance
# :recycle: 			Repost detected

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
import dotmap # Attribute style access to dictionary keys
import bs4 # Parsing & web scraping HTML
import difflib # For computing deltas
import operator # Extra sorting methods

# Console message
print( "Imported modules." )

##############################################
# Load configuration files
##############################################

# Open the settings file
with open( "/srv/conspiracy-ai/config/settings.jsonc", "r" ) as handle:

	# Read all the file contents
	contents = handle.read()

	# Strip all comments
	stripped = re.sub( r"\/\*[^*]*\*\/| ?\/\/.*", "", contents )

	# Parse JSON into a map
	settings = dotmap.DotMap( json.loads( stripped ) )

# Open the secrets file
with open( "/srv/conspiracy-ai/config/secrets.jsonc", "r" ) as handle:

	# Read all the file contents
	contents = handle.read()

	# Strip all comments
	stripped = re.sub( r"\/\*[^*]*\*\/| ?\/\/.*", "", contents )

	# Parse JSON into a map
	secrets = dotmap.DotMap( json.loads( stripped ) )

# Console message
print( "Loaded configuration files." )

##############################################
# Load localisation strings
##############################################

# For all of the localisation strings
strings = {}

# Loop through all files & directories in the strings directory
for name in os.listdir( "/srv/conspiracy-ai/strings" ):

	# Skip if it isn't a regular file
	if not os.path.isfile( "/srv/conspiracy-ai/strings/" + name ): continue

	# Get the name of the locale
	locale = os.path.splitext( name )[ 0 ]

	# Open the file for reading
	with open( "/srv/conspiracy-ai/strings/" + name, "r" ) as handle:

		# Read all the contents of the file
		contents = handle.read()

		# Strip all comments
		stripped = re.sub( r"\/\*[^*]*\*\/| ?\/\/.*", "", contents )

		# Parse the JSON into the main strings dictionary
		strings[ locale ] = json.loads( stripped )

# Console message
print( "Loaded localisation strings." )

##############################################
# Initalise global variables
##############################################

# Cooldowns for anonymous relay
userCooldowns = {}

# The last sent messages for the anonymous relay
lastSentMessage = {}

# When the last dad joke was (default is 60 seconds in the past from now)
lastDadJoke = time.time() - 60

# The choose random activity background task
randomActivityTask = None

# The update server category status background task
updateCategoryTask = None

# Holds the latest status of each server - by default all are nothing
latestServerStatus = { server: None for server in settings.garrysmod.keys() }

# Console message
print( "Initalised global variables." )

##############################################
# Initalise global constants
##############################################

# The current shorthand commit SHA of the local repository
COMMIT = os.popen( "cd /srv/conspiracy-ai && git log --max-count=1 --pretty=format:\"%h\"" ).read()

# User agent header for HTTP requests
USER_AGENT_HEADER = "Conspiracy AI/" + COMMIT + " (GNU/Linux; Discord Bot) Python/" + str( sys.version_info.major ) + "." + str( sys.version_info.minor ) + "." + str( sys.version_info.micro ) + " discord.py/" + discord.__version__ + " (github.com/conspiracy-servers/conspiracy-ai; " + settings.email + ")"

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

# This is the default metadata for chat commands
DEFAULT_COMMAND_METADATA = {

	# The category displayed in the !commands response
	"category": "Other",

	# Additional ways to call/execute the same command (empty list = no aliases)
	"aliases": [],

	# True if the command gives NSFW responses, false otherwise (auto-restricts it to only NSFW channels)
	"nsfw": False,

	# Permissions a member requires to use the command (none = everyone can use/no specific permissions needed)
	"permissions": None,

	# Channels the command can only be used in (empty list = can be used in all channels)
	"channels": [],

	# Roles a member requires to use the command (empty list = any role can use)
	"roles": [],

	# True if the command can only be used in direct messages, false otherwise
	"dm": False,

	# True if the input command/calling action should be deleted after this command is used
	"delete": False,

	# True if the command is work-in-progress, this means it cannot be used by anyone else other than me :)
	"wip": False,

	# The only users who can use this command (empty list = any user can use)
	"users": [],

	# The command's parent command (none = no parent command)
	"parent": None,

	# Additional ways to call/execute the same subcommand (empty list = no aliases, only works if parent is set)
	"subaliases": [],

	# A message explaining the command, showing usage examples, etc. (none = no help available)
	"help": None

}

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
	logsChannel = client.get_channel( settings.channels.logs.id )

	# Create an embed
	embed = discord.Embed( title = title, description = description, color = settings.color )

	# Set the footer to the current date & time
	embed.set_footer( text = formatTimestamp() )

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

# Get the pretty name of a Garry's Mod map
def prettyMapName( genericName ):

	# Split the generic name up every underscore
	parts = genericName.split( "_" )

	# Is there just one part of the generic name?
	if len( parts ) == 1:

		# Return the generic name with a capital start
		return genericName.title()

	# There are multiple parts of the generic name
	else:

		# Convert the gamemode prefix to uppercase
		prefix = parts[ 0 ].upper()

		# Capitalise the start of each word for the rest of the generic name
		theRest = " ".join( parts[ 1: ] ).title()

		# Return both combined
		return prefix + " " + theRest

# Get the message identifier and deletion token for an anonymous message send/delete
def anonymousMessageHashes( anonymousMessage, directMessage ):

	# Store the secret sauce
	secretSauce = secrets.anonymous.sauce

	# The message identifier, soon to be hashed!
	messageIdentifier = str( anonymousMessage.id ).encode( "utf-8" )

	# The deletion token, soon to be hashed!
	deletionToken = ( str( time.mktime( anonymousMessage.created_at.timetuple() ) ) + str( directMessage.author.id ) ).encode( "utf-8" )

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
		host = settings.database.address,
		port = settings.database.port,
		user = secrets.database.user,
		password = secrets.database.passwd,
		database = settings.database.name
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
		"From": settings.email
	} )

	# Create parsing soup from the received HTML
	soup = bs4.BeautifulSoup( vanity.text, features = "html.parser" )

	# Return the found image source URL in html > head > link > image_src
	return soup.find( "link", { "class": "dynamic", "rel": "image_src" } )[ "href" ]

# Download media over HTTP and save it to disk
def downloadWebMedia( originalURL ):

	# Create the downloads directory if it doesn't exist
	if not os.path.isdir( "/srv/conspiracy-ai/downloads" ): os.mkdir( "/srv/conspiracy-ai/downloads", 0o700 )

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
		"From": settings.email
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

	# This is the local file's full path
	path = "/srv/conspiracy-ai/downloads/" + hashedURL + extension

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
		"From": settings.email
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
	path = downloadWebMedia( url )

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

	# Return false if this message's channel is an excluded channel
	if message.channel.id in settings.channels.logs.exclude: return False

	# Return false if this message's channel category is an excluded channel category
	if message.channel.id in settings.channels.logs.exclude: return False

	# Is this not in a log exclusion channel?
	if message.channel.category_id in settings.channels.logs.exclude: return False

	# Return true otherwise
	return True

# Update the locally cached status of a server
async def updateLocalServerStatus( name ):

	# Bring a few global variables into this scope
	global latestServerStatus

	# Construct the API URL of this server
	apiServerURL = "http://" + settings.garrysmod[ name ].address + ":" + str( settings.garrysmod[ name ].port ) + "/info"

	# Be safe!
	try:

		# Fetch current statistics and players from the API
		serverRequest = requests.get( apiServerURL, timeout = 3, headers = {
			"Authorization": secrets[ name ].key,
			"From": settings.email,
			"User-Agent": USER_AGENT_HEADER,
			"Connection": "close"
		} )

	# The server is offline - crashed, shutdown, restarting
	except requests.exceptions.ConnectionError:

		# Update the global latest server status for this server
		latestServerStatus[ name ] = 1

	# The server is frozen - crashed, deadlocked, timing out
	except requests.exceptions.ReadTimeout:

		# Update the global latest server status for this server
		latestServerStatus[ name ] = 2

	# The server is online
	else:

		# Was the request unsuccessful?
		if serverRequest.status_code != 200 or serverRequest.json()[ "success" ] == False:

			# Throw an error
			raise Exception( "Received non-success API response: " + str( serverRequest.status_code ) + "\n" + str( serverRequest.text ) )

		# Parse the response
		server = Server( serverRequest, settings.garrysmod[ name ] )

		# Update the global latest server status for this server
		latestServerStatus[ name ] = server

# Update the status on a server category
async def updateServerCategoryStatusWithLocal( name ):

	# Fetch the server status
	server = latestServerStatus[ name ]

	# Placeholder for the status text
	text = "Unknown"

	# Is the status valid?
	if type( server ) == Server:

		# Store the total number of players currently on the server
		players = len( server.players ) + len( server.admins ) + len( server.bots )

		# Is the server empty?
		if players == 0:

			# Update the status text
			text = "Empty"

		# Is the server full?
		elif players == server.maxPlayers:

			# Update the status text
			text = "Full"

		# The server is between empty and full
		else:

			# Update the status text
			text = str( players ) + " Playing"

	# Is the status 1? - Connection error
	elif server == 1:

		# Update the status text
		text = "Offline"

	# Is the status 2? - Timed out
	elif server == 2:

		# Update the status text
		text = "Crashed"
	
	# Fetch the category channel
	category = client.get_channel( settings.channels.statuses[ name ] )

	# Update the category name
	await category.edit( name = "🔨 Sandbox (" + text + ")", reason = "Update server status in category name." )

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
# Define GMod Relay Classes
##############################################

# Player class
class Player:
	def __init__(self, playerDict, serverConfig):
		self.name = playerDict["name"]
		self.steamID = playerDict["steamid"]
		self.group = playerDict["group"]
		self.userID = round(playerDict["id"])
		self.time = round(playerDict["time"])
		self.timePretty = formatSeconds( self.time )
		self.profileURL = f"https://steamcommunity.com/profiles/{self.steamID}"

		if self.group in serverConfig[ "groups" ]:
			self.groupPretty = serverConfig[ "groups" ][ self.group ]
		else:
			self.groupPretty = self.group

# Bot Class
class Bot:
	def __init__(self, botDict):
		self.name = botDict["name"]
		self.userID = round(botDict["id"])

# Server class
class Server:
	def __init__(self, request, serverConfig):
		response = request.json()["response"]

		self.latency = round( request.elapsed.total_seconds() * 1000 )
		self.hostname = response[ "hostname" ]
		self.gamemode = response[ "gamemode" ]
		self.ipAddress = response[ "ip"]
		self.map = response[ "map" ]
		self.uptime = round( response[ "uptime" ] )
		self.uptimePretty = formatSeconds( self.uptime )
		self.maxPlayers = round( response[ "maxplayers" ] )
		self.mapImage = "https://files.conspiracyservers.com/maps/large/" + response[ "map" ] + ".jpg"
		self.players = [ Player( player, serverConfig ) for player in response[ "players" ] ]
		self.admins = [ Player( admin, serverConfig ) for admin in response[ "admins" ] ]
		self.bots = [ Bot( bot ) for bot in response[ "bots" ] ]
		self.mapPretty = prettyMapName( response[ "map" ] )
		self.mapLink = "https://" + settings.maps[ response[ "map" ] ] if response[ "map" ] in settings.maps else None
		self.tickrate = round( ( 1 / response[ "frametime" ] ), 2 )

# Console message
print( "Defined relay classes." )

##############################################
# Setup the chat commands
##############################################

# A chat command class that inherits from a dictionary
class ChatCommand( dict ):

	# Called when the class is initalised
	def __init__( self, metadata, parentMetadata ):

		# Call the dictionary class' init method
		super( ChatCommand, self ).__init__( metadata )

		# Copy all default command metadata to a local dictionary
		data = DEFAULT_COMMAND_METADATA.copy()

		# Has the parent metadata been provided?
		if parentMetadata:

			# Update the local dictionary with certain metadata properties from the parent command
			data.update( {
				"category": parentMetadata.category,
				"nsfw": parentMetadata.nsfw,
				"permissions": parentMetadata.permissions,
				"channels": parentMetadata.channels,
				"roles": parentMetadata.roles,
				"dm": parentMetadata.dm,
				"delete": parentMetadata.delete,
				"wip": parentMetadata.wip,
				"users": parentMetadata.users,
			} )

		# Update the local dictionary with any metadata passed to this method
		data.update( metadata )

		# Add each key & value pair in the local dictionary to this object
		for key, value in data.items(): self[ key ] = value

	# Called when there is an attempt to get an attribute
	def __getattr__( self, name ):

		# Attempt to fetch the attribute by its name, return none if not found
		return self.get( name, None )

	# Called when there is an attempt to set an attribute
	def __setattr__( self, key, value):

		# Call the dictionary class' set item method with the same arguments
		self.__setitem__( key, value )

	# Called when there is an attempt to delete an attribute
	def __delattr__( self, item ):

		# Call the dictionary class' delete item method with the same arguments
		self.__delitem__( item )

# A class that holds all easily registered chat commands
class ChatCommands:

	# Called when the class is initalised
	def __init__( self ):

		# Create a dictionary to hold the registered/usable chat commands
		self.commands = {}

		# Create a dictionary to hold lookup references for every registered chat command
		self.lookup = {}

	# Called when this object is called like a function
	def __call__( self, **metadata ):

		# Placeholder for the parent metadata
		parentMetadata = None

		# Set the parent metadata to the parent command's metadata if this a subcommand and inheriting from parent is enabled
		if "parent" in metadata and metadata[ "parent" ]: parentMetadata = self.lookup[ metadata[ "parent" ] ]

		# Create a chat command object from the passed metadata and parent metadata (if applicable) as keyword arguments and temporarily store it
		self.command = ChatCommand( metadata, parentMetadata )

		# Return the command register function so the decorator can continue
		return self.register

	# Called to check if an object contains an item (the 'in' statement)
	def __contains__( self, item ):

		# Return a boolean if the queried item is in the registered commands dictionary
		return item in self.commands

	# Called to get an item from this object
	def __getitem__( self, name ):

		# Return the item with the same name in the registered commands dictionary
		return self.commands[ name ]

	# Called when iterating over this obhect
	def __iter__( self ):

		# Return an iterator for the items in the registered commands dictionary
		return iter( self.commands.items() )

	# A function to register new chat commands
	def register( self, function ):

		# Set the chat command object's execute property to the passed function reference
		self.command.execute = function

		# Add an empty dictionary for subcommands to be added to later
		self.command.subcmds = {}

		# Is this a subcommand?
		if self.command.parent:

			# Add the subcommand to the subcmds dictionary of the parent command
			self.lookup[ self.command.parent ].subcmds[ function.__name__ ] = self.command

			# Register all subaliases for this subcommand with their values as a reference to the existing subcommand above
			for name in self.command.subaliases: self.lookup[ self.command.parent ].subcmds[ name ] = self.lookup[ self.command.parent ].subcmds[ function.__name__ ]

			# Register all aliases for this subcommand with their values as a reference to the existing subcommand above
			for name in self.command.aliases: self.commands[ name ] = self.lookup[ self.command.parent ].subcmds[ function.__name__ ]

		# This is not a subcommand
		else:

			# Add the command to the registered commands dictionary by using the function's name as a key
			self.commands[ function.__name__ ] = self.command

			# Register all aliases for this command with their values as a reference to the existing main command above
			for name in self.command.aliases: self.commands[ name ] = self.commands[ function.__name__ ]

		# Register the command/subcommand in the lookup reference dictionary
		self.lookup[ function.__name__ ] = self.command

		# Delete the temporarily stored chat command object
		del self.command

# Inistansiate an object from the chat commands holder class
chatCommands = ChatCommands()

# Create a duplicate reference to the chat commands object for syntatic sugar in the command definition files
chatCommand = chatCommands

# Import each chat command file
from commands import example

#############################################################################################################
######################### ALL THE CHAT COMMANDS BELOW THIS POINT USE THE OLD SYSTEM ######################### 
#############################################################################################################

# A class to hold all the chat commands
class ChatCommandsDeprecated:

	#### Class methods

	# Constructor
	def __init__( self, client ):
		self.client = client # So we don't have to pass the client to every function call

	# Runs when the in operator is used
	def __contains__( self, command ):
		return hasattr( self, command )

	# Runs when the class is indexed like a dictionary
	def __getitem__( self, command ):
		return getattr( self, command )

	# Runs when the class is called like a function (this isn't used rn)
	def __call__( self, command, *arguments, **kwarguments ):
		return getattr( self, command )( *arguments, **kwarguments )

	# Dictionary to hold extra metadata
	metadata = {}

	#### Command definitions

	# Help command
	metadata[ "help" ] = [ "General" ]
	async def help( self, message, arguments, permissions ):

		# Create an embed with help information
		helpEmbed = discord.Embed( title = "", description = "", color = settings.color )

		# About field
		helpEmbed.add_field(
			name = "About the Community",
			value = "Conspiracy Servers is a Garry's Mod community founded by <@" + str( settings.owner ) + "> and <@213413722943651841> in early 2016, we've been going for nearly 5 years now and have always kept our non-serious, relaxed and casual approach towards our community and its servers.",
		)

		# Guidelines & rules field
		helpEmbed.add_field(
			name = "Guidelines & Rules",
			value = "If you're new here or need a refresher on the community's rules and guidelines then please check <#410507397166006274>.",
			inline = False
		)

		# Chat commands field
		helpEmbed.add_field(
			name = "Chat Commands",
			value = "Type `" + settings.prefixDeprecated + "commands` for a list of usable chat commands. Try to keep command usage in <#241602380569772044> to avoid cluttering the discussion channels.",
			inline = False
		)

		# Staff contact field
		helpEmbed.add_field(
			name = "Contacting Staff",
			value = "The ideal way to reach out to our staff is by direct messaging them. You can identify a staff member by checking if they have the <@&613124236101419019> role, they also will display near the top of the members list.",
			inline = False
		)

		# Send the embed back
		await message.channel.send( embed = helpEmbed )

	# Search rule 34 for posts
	metadata[ "rule34" ] = [ "NSFW" ]
	async def rule34( self, message, arguments, permissions ):

		# Is this not being used in an NSFW channel?
		if message.guild != None and not message.channel.is_nsfw():

			# Friendly message
			await message.channel.send( ":exclamation: This command can only be used in channels marked as NSFW." )

			# Prevent further execution
			return

		# Are there no arguments provided?
		if len( arguments ) <= 0:

			# Friendly message
			await message.channel.send( ":grey_exclamation: You must provide at least one tag to search for." )

			# Prevent further execution
			return

		# Construct API search URL
		tagsQuery = "%20".join( arguments )
		apiURL = "https://rule34.xxx/index.php?page=dapi&s=post&q=index&limit=100&tags=" + tagsQuery + "%20-loli%20-shota"

		# Make the API search request
		searchRequest = requests.get( apiURL, headers = {
			"Accept": "application/xml",
			"From": settings.email,
			"User-Agent": USER_AGENT_HEADER
		} )

		# Was the request unsuccessful?
		if searchRequest.status_code != 200:

			# Throw an error
			raise Exception( "Received non-success API response: " + str( searchRequest.status_code ) + "\n" + str( searchRequest.text ) )

		# Parse the XML response
		root = xml.etree.ElementTree.fromstring( searchRequest.text )

		# Put each child element into a list
		posts = [ child for child in root ]

		# Did we get no results?
		if len( posts ) <= 0:

			# Friendly message
			await message.channel.send( ":mag_right: I wasn't able to find anything matching the provided tags." )

			# Prevent further execution
			return

		# Sort the responses from highest to lowest score
		posts.sort( reverse = True, key = lambda post: int( post.get( "score" ) ) )

		# Pick a random post from the top 10
		post = random.choice( posts[ :10 ] )

		# Download the post file
		path = downloadWebMedia( post.get( "file_url" ) )

		# Was the file not downloaded?
		if path == None:

			# Friendly message with a link to the source file
			await message.channel.send( ":interrobang: I was't able to download the post.\nScore: " + post.get( "score" ) + ".\n||" + post.get( "file_url" ) + "||" )

			# Prevent further execution
			return

		# Is the file's size greater than 8MB (~8,388,119 bytes)? - See redd.it/aflp3p
		if os.path.getsize( path ) > 8388119:

			# Send back a message with the file link inline
			await message.channel.send( "Score: " + post.get( "score" ) + ".\n||" + post.get( "file_url" ) + "||" )

			# Prevent further execution
			return

		# Get the file extension
		extension = os.path.splitext( path )[ 1 ]

		# The name for the file when uploaded to Discord
		discordFileName = post.get( "md5" ) + extension

		# Create a discord file object marked as spoiler
		postFile = discord.File( path, filename = discordFileName, spoiler = True )

		# Be safe!
		try:

			# Send back a message with the file as an attachment
			await message.channel.send( "Score: " + post.get( "score" ) + ".", file = postFile )
		
		# Catch discord errors
		except discord.HTTPException as exception:

			# Is the error for the file being to large?
			if exception.code == 40005:

				# Message with spoilered link to source file
				await message.channel.send( ":interrobang: The post is too large to upload.\nScore: " + post.get( "score" ) + ".\n||" + post.get( "file_url" ) + "||" )

			# The error is something else
			else:

				# Re-raise the exception for somebody else to deal with
				raise exception

	# Alias for rule 34 command
	async def r34( self, *arguments, **kwarguments ):
		return await self.rule34( *arguments, **kwarguments )

	# List all the available chat commands
	metadata[ "commands" ] = [ "General" ]
	async def commands( self, message, arguments, permissions ):

		# A dictionary for the chat commands and each of their aliases
		availableChatCommands = { metadata[ 0 ] : {} for command, metadata in self.metadata.items() }

		# Loop through all properties and methods of this class
		for definition in dir( self ):

			# Get the method
			method = getattr( self, definition )

			# Skip if it's not a callable method
			if not callable( method ): continue

			# Skip if it's an internal/class method
			if definition.startswith( "__" ): continue

			# Skip if it's this command
			if definition == "commands" or definition == "cmds": continue

			# Inspect the method's code to see if it matches the alias regex pattern 
			inspection = re.search( r"return await self\.(\w+)\( \*\w+, \*\*\w+ \)", inspect.getsource( method ) )

			# Is it an alias?
			if inspection != None:

				# Get the real command this alias is for
				realCommand = inspection.group( 1 )

				# Get the real command's category
				category = self.metadata[ realCommand ][ 0 ]

				# Has the real command already been added to this category?
				if realCommand in availableChatCommands[ category ]:

					# Append the alias to the real command
					availableChatCommands[ category ][ realCommand ].append( definition )

				# The real command has not been added to it's category yet
				else:

					# Add the real command with this alias as a list
					availableChatCommands[ category ][ realCommand ] = [ definition ]

			# It's a real command and it isn't already in the list
			elif inspection == None and definition not in availableChatCommands:

				# Get the real command's category
				category = self.metadata[ definition ][ 0 ]

				# Has the real command not already been added to this category?
				if definition not in availableChatCommands[ category ]:
	
					# Add the real command with an empty list for future aliases
					availableChatCommands[ category ][ definition ] = []

		# Create a blank embed to be updated soon
		embed = discord.Embed( title = "Chat Commands", description = "", color = settings.color )

		# Loop through all of the available chat command categories and their commands
		for category, commands in availableChatCommands.items():

			# Placeholder for the value of this embed field
			value = ""

			# Loop through all of the available chat commands
			for command, aliases in commands.items():

				# Construct a string out of the list of command aliases
				aliasesString = " *(" + ", ".join( [ "`" + settings.prefixDeprecated + alias + "`" for alias in aliases ] ) + ")*"

				# Append the command name and it's aliases (if any are available) to the final embed description
				value += "• `" + settings.prefixDeprecated + command + "`" + ( aliasesString if len( aliases ) > 0 else "" ) + "\n"

			# Add the field to the embed for this category
			embed.add_field( name = "__" + category + "__", value = value, inline = False )

		# Send the embed back
		await message.channel.send( embed = embed )

	# Alias for commands command
	async def cmds( self, *arguments, **kwarguments ):
		return await self.commands( *arguments, **kwarguments )

	# Shutdown the bot
	metadata[ "shutdown" ] = [ "Administration" ]
	async def shutdown( self, message, arguments, permissions ):

		# Does the user not have the administrate permission?
		if not permissions.administrator:

			# Feedback message
			await message.channel.send( ":no_entry_sign: This command can only be used by administrators." )

			# Prevent further execution
			return

		# Log the event
		await log( "Bot shutdown", "The bot was shutdown by " + message.author.mention )

		# Delete the shutdown message
		await message.delete()

		# Sleep for 2 seconds
		await asyncio.sleep( 2 )

		# Logout & disconnect
		await client.logout()
		await client.close()

	# Sandbox server status
	metadata[ "sandbox" ] = [ "Garry's Mod" ]
	async def sandbox( self, message, arguments, permissions ):

		# Bring a few global variables into this scope
		global latestServerStatus

		# Update the local server status cache
		await updateLocalServerStatus( "sandbox" )

		# Fetch the server status
		server = latestServerStatus[ "sandbox" ]

		# Create a blank embed to be used later
		embed = discord.Embed( title = "", description = "", color = 0xF9A507 )

		# Is the status valid?
		if type( server ) == Server:

			# Status
			status = [
				"• Map: " + ( "[" + server.mapPretty + "](" + server.mapLink + ")" if server.mapLink != None else server.mapPretty ),
				f"• Players: { len( server.players ) + len( server.admins ) + len( server.bots ) } / { server.maxPlayers }",
				f"• Latency: { server.latency }ms",
				f"• Tickrate: { server.tickrate }/s",
				f"• Uptime: { server.uptimePretty }",
				f"• IP: [`sandbox.conspiracyservers.com:27045`](https://conspiracyservers.com/join-sandbox)"
			]

			# Useful links
			links = [
				"• [Collection](https://conspiracyservers.com/sandbox)",
				"• [Rules](https://raw.githubusercontent.com/conspiracy-servers/information/master/Sandbox%20Rules.txt)",
				"• [Guidelines](https://raw.githubusercontent.com/conspiracy-servers/information/master/Sandbox%20Guidelines.txt)"
			]

			# Online staff
			players = [ f"• ({ staff.groupPretty }) [{ staff.name }]({ staff.profileURL }) for { staff.timePretty }" for staff in server.admins ]

			# Online players
			for player in server.players: players.append( f"• ({ player.groupPretty }) [{ player.name }]({ player.profileURL }) for { player.timePretty }" )

			# Online bots
			for bot in server.bots: players.append( f"• { bot.name }" )

			# Set the author to the server hostname & icon
			embed.set_author(
				name = server.hostname[:48] + "...",
				icon_url = "https://files.conspiracyservers.com/icons/hammer.png"
			)

			# Set the thumbnail to the map preview
			embed.set_thumbnail( url = server.mapImage )

			# Add a field for current status
			embed.add_field(
				name = "__Status__",
				value = "\n".join( status ),
				inline = True
			)

			# Add a field for useful links
			embed.add_field(
				name = "__Links__",
				value = "\n".join( links ),
				inline = True
			)

			# Are there any players online?
			if len( players ) > 0:

				# Add a field for the currently online players
				embed.add_field(
					name = f"__Players__",
					value = "\n".join( players ),
					inline = False
				)

		# Is the status 1? - Connection error
		elif server == 1:

			# Set the embed title
			embed.title = "Sandbox"

			# Set the embed description
			embed.description = "The server is currently offline."

			# Set the embed color
			embed.color = 0xFF0000

			# Set the embed footer
			embed.set_footer( text = "Connection failed (the server is likely restarting from a recoverable crash)." )

		# Is the status 2? - Timed out
		elif server == 2:

			# Set the embed title
			embed.title = "Sandbox"

			# Set the embed description
			embed.description = "The server is currently offline."

			# Set the embed color
			embed.color = 0xFF0000

			# Set the embed footer
			embed.set_footer( text = "Connection timed out (the server is likely frozen in a non-recoverable state)." )

		# Who knows??
		else:

			# Set the embed title
			embed.title = "Sandbox"

			# Set the embed description
			embed.description = "Tell <@" + str( settings.owner ) + "> that he's forgotten to add a case in the sandbox status command for a new invalid exception he added at some point.\n\nI've been given data that I have no clue what to do with, send help."

		# Send the embed
		await message.channel.send( embed = embed )

		# Update the category status too
		await updateServerCategoryStatusWithLocal( "sandbox" )

	# Alias for sandbox command
	async def sbox( self, *arguments, **kwarguments ):
		return await self.sandbox( *arguments, **kwarguments )

	# Get weather data for a location
	metadata[ "weather" ] = [ "General" ]
	async def weather( self, message, arguments, permissions ):

		# Are there no arguments provided?
		if len( arguments ) <= 0:

			# Friendly message
			await message.channel.send( ":grey_exclamation: You must specify a location to fetch weather information for." )

			# Prevent further execution
			return

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
			await message.channel.send( ":mag_right: I wasn't able to find weather data for a location with that name." )

			# Prevent further execution
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

		# Send the embed back
		await message.channel.send( embed = embed )

	# Get the time in a specific timezone
	metadata[ "time" ] = [ "General" ]
	async def time( self, message, arguments, permissions ):

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

			# Friendly message
			await message.channel.send( ":grey_question: That doesn't appear to be a valid timezone name or identifier." )

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

			# Send a message back
			await message.channel.send( ":calendar: " + timezonePretty )

	# Alias for the time command
	async def date( self, *arguments, **kwarguments ):
		return await self.time( *arguments, **kwarguments )

	# Website link
	metadata[ "website" ] = [ "Links" ]
	async def website( self, message, arguments, permissions ):

		# Friendly message
		await message.channel.send( ":link: The community website is available at https://conspiracyservers.com" )

	# Alias for website command
	async def site( self, *arguments, **kwarguments ):
		return await self.website( *arguments, **kwarguments )

	# Steam group link
	metadata[ "steamgroup" ] = [ "Links" ]
	async def steamgroup( self, message, arguments, permissions ):

		# Friendly message
		await message.channel.send( ":link: The community Steam Group is available at https://conspiracyservers.com/steam" )

	# Alias for Steam group command
	async def steam( self, *arguments, **kwarguments ):
		return await self.steamgroup( *arguments, **kwarguments )

	# Discord invite link
	metadata[ "discord" ] = [ "Links" ]
	async def discord( self, message, arguments, permissions ):

		# Friendly message
		await message.channel.send( ":link: The community Discord invite link is https://conspiracyservers.com/discord" )

	# Alias for Discord command
	async def invite( self, *arguments, **kwarguments ):
		return await self.discord( *arguments, **kwarguments )

	# Staff application link
	metadata[ "staffapplication" ] = [ "Links" ]
	async def staffapplication( self, message, arguments, permissions ):

		# Friendly message
		await message.channel.send( ":link: You can apply for Staff by filling out the application available at https://conspiracyservers.com/apply" )

	# Alias for staff application command
	async def apply( self, *arguments, **kwarguments ):
		return await self.staffapplication( *arguments, **kwarguments )

	# Timeout a user
	metadata[ "timeout" ] = [ "Moderation" ]
	async def timeout( self, message, arguments, permissions ):

		# Does the user not have the manage messages permission?
		if not permissions.manage_messages:

			# Feedback message
			await message.channel.send( ":no_entry_sign: This command can only be used by staff members." )

			# Prevent further execution
			return

		# Was there no mentions?
		if len( message.mentions ) < 1:

			# Friendly message
			await message.channel.send( ":grey_exclamation: You must mention at least one member." )

			# Prevent further execution
			return

		# Fetch the timeout role
		timeoutRole = message.channel.guild.get_role( settings.roles.timeout )

		# Loop through every mentioned member
		for member in message.mentions:

			# Give the member the timeout role
			await member.add_roles( timeoutRole, reason = "Member timed out by " + str( message.author ) )
		
			# Send message feedback
			await message.channel.send( "Timed out " + member.mention + " indefinitely." )

	# Remove a user from timeout
	metadata[ "untimeout" ] = [ "Moderation" ]
	async def untimeout( self, message, arguments, permissions ):

		# Does the user not have the manage messages permission?
		if not permissions.manage_messages:

			# Feedback message
			await message.channel.send( ":no_entry_sign: This command can only be used by staff members." )

			# Prevent further execution
			return

		# Was there no mentions?
		if len( message.mentions ) < 1:

			# Friendly message
			await message.channel.send( ":grey_exclamation: You must mention at least one member." )

			# Prevent further execution
			return

		# Fetch the timeout role
		timeoutRole = message.channel.guild.get_role( settings.roles.timeout )

		# Loop through every mentioned member
		for member in message.mentions:

			# Are they using it on themselves?
			if member.id == message.author.id:
				
				# Friendly message
				await message.channel.send( ":no_entry_sign: You cannot remove yourself from timeout." )

				# Prevent further execution
				return

			# Remove the timeout role from the member
			await member.remove_roles( timeoutRole, reason = "Member removed from timeout by " + str( message.author ) )
		
			# Send message feedback
			await message.channel.send( "Removed " + member.mention + " from timeout." )

	# Lookup information about an anime on My Anime List
	metadata[ "myanimelist" ] = [ "General" ]
	async def myanimelist( self, message, arguments, permissions ):

		# Was there no anime name provided?
		if len( arguments ) < 1:

			# Friendly message
			await message.channel.send( ":grey_exclamation: You must specify the name of an anime to fetch information about." )

			# Prevent further execution
			return

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
			await message.channel.send( ":mag_right: I wasn't able to find an anime with that name." )

			# Prevent further execution
			return

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

		# Send the embed back
		await message.channel.send( embed = embed )

	# Aliases for the anime command
	async def mal( self, *arguments, **kwarguments ):
		return await self.myanimelist( *arguments, **kwarguments )

	async def anime( self, *arguments, **kwarguments ):
		return await self.myanimelist( *arguments, **kwarguments )

	async def manga( self, *arguments, **kwarguments ):
		return await self.myanimelist( *arguments, **kwarguments )

	# Delete message sent in anonymous
	metadata[ "delete" ] = [ "General" ]
	async def delete( self, message, arguments, permissions ):

		# Is this not being used in a direct message?
		if message.guild != None:

			# Friendly message
			await message.channel.send( ":exclamation: To protect your anonyminity, this command should only be used in Direct Messages with me." )

			# Prevent further execution
			return

		# Was there no anime name provided?
		if len( arguments ) < 1:

			# Friendly message
			await message.channel.send( ":grey_exclamation: You must specify the ID of the <#" + str( settings.channels.anonymous ) + "> message to delete.", delete_after = 10 )

			# Prevent further execution
			return

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
			await message.channel.send( ":mag_right: I wasn't able to find a <#" + str( settings.channels.anonymous ) + "> message with that ID.", delete_after = 10 )

		# The specified ID wasn't really an ID
		except ValueError:

			# Friendly message
			await message.channel.send( ":grey_question: That doesn't appear to be a valid message ID.", delete_after = 10 )

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
				await message.channel.send( ":no_entry_sign: The message has not been deleted because your ownership of it could not be verified.\n(Please note, <#" + str( settings.channels.anonymous ) + "> messages sent before the 22nd July 2020 cannot be deleted as no ownership information exists for them.)", delete_after = 10 )

				# Prevent further execution
				return

			# Delete the message from the anonymous channel
			await anonymousMessage.delete()

			# Remove the record from the database
			mysqlQuery( "DELETE FROM AnonMessages WHERE Message = '" + messageIdentifier + "' AND Token = '" + deletionTokenAttempt + "';" )

			# Friendly message
			await message.channel.send( ":white_check_mark: The message has been successfully deleted.", delete_after = 10 )

	# View personal member statistics
	metadata[ "statistics" ] = [ "General" ]
	async def statistics( self, message, arguments, permissions ):

		# Fetch this member's statistics
		statistics = mysqlQuery( "SELECT Messages, Edits FROM MemberStatistics WHERE Member = LOWER( HEX( AES_ENCRYPT( '" + str( message.author.id ) + "', UNHEX( SHA2( '" + secrets.encryptionKeys.memberStatistics + "', 512 ) ) ) ) );" )[ 0 ]

		# Format each statistic
		messages = "{:,}".format( statistics[ 0 ] )
		edits = "{:,}".format( statistics[ 1 ] )

		# Send back a message
		await message.channel.send( ":bar_chart: You have sent a total of **" + messages + "** messages in this server & made **" + edits + "** edits to your own messages.\n*(Statistics from before 02/08/2020 07:01:05 UTC may not be 100% accurate)*" )

	# Alias for statistics command
	async def stats( self, *arguments, **kwarguments ):
		return await self.statistics( *arguments, **kwarguments )

	# View the top member statistics
	metadata[ "topstatistics" ] = [ "General" ]
	async def topstatistics( self, message, arguments, permissions ):

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

		# Send the embed back
		await message.channel.send( embed = embed )

	# Aliases for top member statistics command
	async def topstats( self, *arguments, **kwarguments ):
		return await self.topstatistics( *arguments, **kwarguments )

	async def leaderboard( self, *arguments, **kwarguments ):
		return await self.topstatistics( *arguments, **kwarguments )

	# View the date & time you joined
	metadata[ "joined" ] = [ "General" ]
	async def joined( self, message, arguments, permissions ):

		# Fetch this date & time the member joined
		joinedAt = mysqlQuery( "SELECT Joined FROM Members WHERE Member = LOWER( HEX( AES_ENCRYPT( '" + str( message.author.id ) + "', UNHEX( SHA2( '" + secrets.encryptionKeys.members + "', 512 ) ) ) ) );" )[ 0 ][ 0 ]

		# Fetch the appropriate day suffix
		daySuffix = DAY_SUFFIXES.get( joinedAt.day, "th" )

		# Construct a formatting template using the day suffix
		template = "%A %-d" + daySuffix + " of %B %Y at %-H:%M:%S"

		# Get the pretty date & time
		joinedAtPretty = joinedAt.strftime( template )

		# Send a message back
		await message.channel.send( ":date: You joined this Discord server on **" + joinedAtPretty + "**.\n*(Information from before 08/08/2020 UTC may not be 100% accurate.)*" )

# Console message
print( "Defined chat commands." )

##############################################
# Initalise the client
##############################################

# Create the client
client = discord.Client(

	# Set initial status to idle to indicate not ready yet
	status = discord.Status.dnd if len( sys.argv ) > 1 else discord.Status.idle,
	
	# Max messages to cache internally
	max_messages = 10000,
	
	# Cache members that are offline
	fetch_offline_members = True,

	# Set the default allowed mentions for each message sent by the bot
	allowed_mentions = discord.AllowedMentions(

		# Disable @everyone & @here pings
		everyone = False,

		# Disable user pings
		users = False,

		# Disable role pings
		roles = False

	)

)

# Instansiate the chat commands class
chatCommandsDeprecated = ChatCommandsDeprecated( client )

# Console message
print( "Connecting to Discord..." )

##############################################
# Define background tasks
##############################################

# Automatically randomise the client's activity
async def chooseRandomActivity():

	# Loop forever
	while not client.is_closed() and client.is_ready():

		# Choose a random activity
		activity = random.choice( settings.activities )

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

# Automatically update the status of the server categories - this is basically a wrapper function
async def updateCategoryStatus():

	# Loop forever
	while not client.is_closed() and client.is_ready():

		# Update the local server status cache
		await updateLocalServerStatus( "sandbox" )

		# Call the helper function
		await updateServerCategoryStatusWithLocal( "sandbox" )

		# Run this again in 1 minute
		await asyncio.sleep( 60 )

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
	global randomActivityTask, updateCategoryTask

	# Launch background tasks - keep this the same as on_ready()!
	randomActivityTask = client.loop.create_task( chooseRandomActivity() )
	updateCategoryTask = client.loop.create_task( updateCategoryStatus() )
	print( "Launched background tasks." )

	# Console message
	print( "Resumed connection to Discord." )

# Runs when the client disconnects
async def on_disconnect():

	# Bring some global variables into this scope
	global randomActivityTask, updateCategoryTask

	# Cancel tasks
	randomActivityTask.cancel()
	updateCategoryTask.cancel()
	print( "Cancelled background tasks." )

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
	guildMember = discord.utils.get( client.get_guild( settings.guild ).members, id = message.author.id )

	# Ignore direct messages if the author isn't in the discord server
	if message.guild == None and guildMember == None:

		# Friendly message
		await message.author.dm_channel.send( ":exclamation: You must be a member of the Conspiracy Servers Discord to use me.\nJoin here: https://conspiracyservers.com/discord", delete_after = 60 )

		# Prevent further execution
		return

	# Is the message just a ping to the bot?
	if message.content == client.user.mention:

		# Friendly message
		await message.channel.send( ":information_source: Type `" + settings.prefixDeprecated + "commands` to view a list of commands." )

		# Prevent further execution
		return

	# Escape markdown and remove pings
	safeContent = discord.utils.escape_markdown( message.clean_content )

	# Extract all links from the message's content
	inlineURLs = re.findall( r"(https?://[^\s]+)", message.content )

	# Get all attachment links from attachments with the message
	attachmentURLs = [ attachment.url for attachment in message.attachments ]

	# Store the current unix timestamp for later use
	unixTimestampNow = time.time()

	# Is this message an old chat command?
	if message.content.startswith( settings.prefixDeprecated ):
	
		# Get both the command and the arguments
		command = ( message.content.lower()[ 1: ].split( " " )[ 0 ] if message.content.lower()[ 1: ] != "" else None )

		# If there's no command, stop execution
		if command == None: return

		# Start typing in the channel
		await message.channel.trigger_typing()

		# Is the chat command valid?
		if command in chatCommandsDeprecated:

			# Create the list of arguments
			arguments = message.clean_content[ len( command ) + 2 : ].split()
			
			# Default to guild permissions
			permissions = guildMember.guild_permissions

			# Is this a message from a guild?
			if message.guild != None:

				# Use channel permissions instead
				permissions = message.author.permissions_in( message.channel )

			# Be safe!
			try:

				# Execute the command
				await chatCommandsDeprecated[ command ]( message, arguments, permissions )

			# Catch all errors that occur
			except Exception:

				# Print a stacktrace
				print( traceback.format_exc() )

				# Friendly message
				await message.channel.send( ":interrobang: Something really, *really* bad happened while trying to execute that command and I have no idea what to do now." )

			finally:

				# Should we log this command usage?
				if shouldLog( message ):

					# Console message
					print( "(" + ascii( message.channel.category.name ) + " -> #" + message.channel.name + ") " + str( message.author ) + " (" + message.author.display_name + "): " + message.content )

					# Log the usage of the command
					await log( "Command executed", message.author.mention + " executed the `" + command + "` command" + ( " with arguments `" + " ".join( arguments ) + "`" if len( arguments ) > 0 else "" ) + " in " + message.channel.mention, jump = message.jump_url )

		# Unknown chat command
		else:

			# Friendly message
			await message.channel.send( ":grey_question: I didn't recognise that command, type `" + settings.prefixDeprecated + "commands` to see a list of available chat commands.", delete_after = 10 )

	# Is this message a new chat command?
	elif message.content.startswith( settings.prefix ):
	
		# Get both the command and the arguments
		command = ( message.content.lower()[ 1: ].split( " " )[ 0 ] if message.content.lower()[ 1: ] != "" else None )

		# Prevent further execution if there's no command
		if command == None: return

		# Start typing in the channel
		await message.channel.trigger_typing()

		# Is the chat command valid?
		if command in chatCommands:

			# Fetch the command metadata
			metadata = chatCommands[ command ]

			# Create the list of arguments
			arguments = message.content[ len( command ) + 2 : ].split()

			# Loop so long as there is at least one argument
			while len( arguments ) > 0:

				# Is the first argument a subcommand?
				if arguments[ 0 ] in metadata.subcmds:

					# Update the command variable to the first argument
					command = arguments[ 0 ]

					# Remove the command from the arguments
					del arguments[ 0 ]

					# Fetch the subcommand metadata
					metadata = metadata.subcmds[ command ]

				# It's not a subcommand
				else:

					# Break out of the loop
					break

			# Is this command work-in-progress & is the author not me?
			if metadata.wip and message.author.id != settings.owner:

				# Give a response
				await message.channel.send( ":wrench: This command is work-in-progress, please refrain from using it until it's released." )

				# Prevent further execution
				return

			# Is this command restricted to certain users & is this user not one of them?
			if len( metadata.users ) > 0 and message.author.id not in metadata.users:

				# Convert the list of users to a clean string
				users = ", ".join( [ client.get_user( userID ).mention for userID in metadata.users ] )

				# Give a response
				await message.channel.send( ":no_entry_sign: This command can only be used by " + users + "." )

				# Prevent further execution
				return

			# Is this command DM only & is this not a direct message?
			if metadata.dm and message.guild:

				# Give a response
				await message.channel.send( ":exclamation: This command can only be used over Direct Messages." )

				# Prevent further execution
				return

			# Is this not a direct message?
			if message.guild:

				# Is this command NSFW & is this not an NSFW channel?
				if metadata.nsfw and not message.channel.is_nsfw():

					# Give a response
					await message.channel.send( ":exclamation: This command can only be used in NSFW channels." )

					# Prevent further execution
					return

				# Is this command only available in certain channels and is this not one of those channels?
				if len( metadata.channels ) > 0 and message.channel.id not in metadata.channels:

					# Convert the list of channels to a clean string
					channels = ", ".join( [ client.get_channel( channelID ).mention for channelID in metadata.channels ] )

					# Give a response
					await message.channel.send( ":exclamation: This command can only be used in " + channels + "." )

					# Prevent further execution
					return

			# Create a list of the role IDs this member has
			roleIDs = [ role.id for role in guildMember.roles ]

			# Create a list of the roles this member requires to execute this command (if there are any)
			requiredRoles = [ message.guild.get_role( roleID ) for roleID in metadata.roles if roleID not in roleIDs ]

			# Is there at least one additional role that this member requires?
			if len( requiredRoles ) > 0:

				# Convert the list of roles to a clean string
				roles = ", ".join( [ role.mention for role in requiredRoles ] )

				# Give a response
				await message.channel.send( ":no_entry_sign: This command can only be used by members with the role " + roles + "." )

				# Prevent further execution
				return

			# Use channel permissions if this message is not from direct messages, otherwise use overall guild permissions
			#permissions = ( message.author.permissions_in( message.channel ) if message.guild else guildMember.guild_permissions )

			# Does this command require certain permissions and does this member not have those permissions?
			#if metadata.permissions and permissions < metadata.permissions:

				# Give a response
				#await message.channel.send( ":no_entry_sign: You don't have the necessary permissions to use this command." )

				# Prevent further execution
				#return

			# Delete the command caller/input if it's set to do so
			if metadata.delete: await message.delete()

			# Be safe!
			try:

				# Execute the command and store it's response
				response = await metadata.execute( message, arguments )

			# Catch all errors that occur
			except Exception:

				# Print a stacktrace
				print( traceback.format_exc() )

				# Friendly message
				await message.channel.send( ":interrobang: I encountered an error while attempting to execute that command, <@" + str( settings.owner ) + "> needs to fix this.", allowed_mentions = ALLOW_USER_MENTIONS )

			# No errors occured
			else:

				# Send a response with user mention capability if it was provided
				if response != None: await message.channel.send( **response, allowed_mentions = ALLOW_USER_MENTIONS )

			# We're done here
			finally:

				# Don't continue if this is a direct message - I respect privacy!
				if not message.guild: return

				# Display a console message
				print( "(" + ascii( message.channel.category.name ) + " -> #" + message.channel.name + ") " + str( message.author ) + " (" + message.author.display_name + ") executed command '" + command + "'" + ( " with arguments '" + ", ".join( arguments ) + "'" if len( arguments ) > 0 else "" ) + "." )

				# Don't continue if the channel is an excluded channel
				if message.channel.id in settings.channels.logs.exclude: return

				# Don't continue if this channel's category is an excluded channel category
				if message.channel.category_id in settings.channels.logs.exclude: return

				# Log the usage of the command
				await log( "Command executed", message.author.mention + " executed command `" + command + "`" + ( " with arguments `" + " ".join( arguments ) + "`" if len( arguments ) > 0 else "" ) + " in " + message.channel.mention, jump = message.jump_url )

		# Unknown chat command
		else:

			# Calculate the ratio of how similar the attempted command is to all other commands
			similarMatches = { name : difflib.SequenceMatcher( None, command, name ).ratio() for name, metadata in chatCommands } # WHEN RELEASING ADD: 'if not metadata.wip'

			# Sort by the highest ratio (the most accurate/similar match)
			sortedSimilarMatches = sorted( similarMatches, key = similarMatches.get, reverse = True )

			# Send back a message
			await message.channel.send( ":grey_question: I didn't recognise that command, " + ( "did you mean `" + settings.prefix + sortedSimilarMatches[ 0 ] + "`? If not, " if len( sortedSimilarMatches ) > 0 else "" ) + "type `" + settings.prefix + "commands` to see a list of commands." )

	# This message is not a chat command
	else:

		# Is this message sent from a guild?
		if message.guild != None:

			# Console message
			print( "(" + ascii( message.channel.category.name ) + " -> #" + message.channel.name + ") " + str( message.author ) + " (" + message.author.display_name + "): " + message.content + ( "\n\t".join( attachmentURLs ) if len( attachmentURLs ) > 0 else "" ) )

			# Create or increment the message sent statistic for this member
			mysqlQuery( "INSERT INTO MemberStatistics ( Member ) VALUES ( LOWER( HEX( AES_ENCRYPT( '" + str( message.author.id ) + "', UNHEX( SHA2( '" + secrets.encryptionKeys.memberStatistics + "', 512 ) ) ) ) ) ) ON DUPLICATE KEY UPDATE Messages = Messages + 1;" )

			# Are we not in a repost excluded channel?
			if message.channel.id not in settings.reposts.exclude:

				# Loop through all of those inline links and attachment links
				for url in itertools.chain( attachmentURLs, inlineURLs ):

					# Get any repost information
					repostInformation = isRepost( url )

					# Skip if the information is nothing - this means the link is not an image/video/audio file, or is over 100 MiB
					if repostInformation == None: continue

					# Skip if this checksum is in the repost exclude list
					if repostInformation[ 1 ] in settings.reposts.excludeChecksums: continue

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

								# Friendly message
								await message.channel.send( "> <" + url + ">\n:recycle: " + message.author.mention + " this could be a repost, I've seen it " + str( repostInformation[ 2 ] ) + " time(s) before. The original post: <https://discordapp.com/channels/" + str( settings.guild ) + "/" + str( repostInformation[ 0 ] ) + "/" + str( repostInformation[ 1 ] ) + ">.", allowed_mentions = ALLOW_USER_MENTIONS )

			# Does the message start with "Im " and has it been 15 seconds since the last one?
			if message.content.startswith( "Im " ) and ( lastDadJoke + 15 ) < unixTimestampNow:
	
				# Send dadbot response
				await message.channel.send( "Hi " + message.clean_content[ 3: ] + ", I'm dad!" )

				# Set the last dad joke date & time
				lastDadJoke = unixTimestampNow

			# Are we sending a message in a relay channel?
			if str( message.channel.id ) in settings.channels.relays.keys():

				# Placeholder for the message that will be sent
				relayContent = message.clean_content

				# Remove emojis from the message
				relayContent = re.sub( r"<a?:([A-Za-z0-9_-]+):\d{18}\\?>", r":\1:", relayContent )

				# Remove newlines from the message
				relayContent = re.sub( r"\n", " ", relayContent )

				# Loop through all attachments
				for attachment in message.attachments:

					# Download the attachment
					path = downloadWebMedia( attachment.url )

					# Skip if the download failed
					if path == None: continue

					# Get the checksum of the file contents
					checksum = fileChecksum( path )

					# Query the database to fetch the link for this attachment
					result = mysqlQuery( "SELECT Link FROM RelayShortlinks WHERE Checksum = '" + checksum + "';" )

					# Placeholder for the shortlink
					shortlink = ""

					# Does it not exist in the database?
					if len( result ) > 0:
						
						# Set the shortlink to the result from the database query
						shortlink = "https://bit.ly/" + result[ 0 ][ 0 ]

					# It does not exist in the database
					else:

						# Query the bit.ly and create a new link
						bitlyRequest = requests.post( "https://api-ssl.bitly.com/v4/shorten", headers = {
							"Accept": "application/json",
							"Content-Type": "application/json",
							"Authorization": "Bearer " + secrets.bitly.key,
							"User-Agent": USER_AGENT_HEADER,
							"From": settings.email
						}, json = {
							"long_url": attachment.url,
							"tags": [ "Discord Relay" ]
						} )

						# Set the shortlink to the newly created bit.ly link from the response
						shortlink = bitlyRequest.json()[ "link" ]

						# Remove the schema and host from the shortlink
						identifier = shortlink.replace( "https://bit.ly/", "" )

						# Add it to the database
						mysqlQuery( "INSERT INTO RelayShortlinks ( Checksum, Link ) VALUES ( '" + checksum + "', '" + identifier + "' );" )

					# Append the shortlink to to the message that will be sent
					relayContent += ( " " if len( relayContent ) > 0 else "" ) + shortlink

				# Is their message 127+ characters?
				if len( relayContent ) >= 127:

					# Friendly message
					await message.channel.send( ":grey_exclamation: Your message is too long to be relayed, please shorten it to below 127 characters (attachments count towards this limit.)", delete_after = 10 )

					# Prevent further execution
					return

				# Get the config for this server
				server = settings.garrysmod[ settings.channels.relays[ str( message.channel.id ) ] ]

				# Construct the API's URL
				apiURL = "http://" + server[ "address" ] + ":" + str( server[ "port" ] ) + "/discord"

				# Store the color of their role
				roleColor = message.author.top_role.colour

				# Construct the request payload
				payload = {
					"message": relayContent,
					"author": message.author.display_name,
					"role": {
						"name": message.author.top_role.name,
						"color": [ roleColor.r, roleColor.g, roleColor.b ]
					}
				}

				# Be safe!
				try:

					# Send the message to the API
					requests.post( apiURL, json = payload, timeout = 2, headers = {
						"Accept": "application/json",
						"Authorization": secrets.sandbox.key,
						"From": settings.email,
						"User-Agent": USER_AGENT_HEADER
					} )

				# The server is offline - crashed, shutdown, restarting
				except requests.exceptions.ConnectionError:

					# Friendly message
					await message.channel.send( ":interrobang: Your message was not relayed because the server is currently offline (shutdown/changing map/restarting).", delete_after = 10 )

				# The server is frozen - crashed, deadlocked, timing out
				except requests.exceptions.ReadTimeout:

					## Friendly message
					await message.channel.send( ":interrobang: Your message was not relayed because the connection to the server timed out (crashed/frozen/locked up).", delete_after = 10 )

		# This message was sent over direct messages
		else:

#############################################################################################################
######################### ALL CODE BELOW THIS LINE NEEDS REFORMATTING & CLEANING UP ######################### 
#############################################################################################################

			guild = client.get_guild( settings.guild )

			_webhooks=await guild.webhooks()
			anonymousWebhook=discord.utils.get(_webhooks,name="Anonymous")

			memberRole=discord.utils.get(guild.roles,name="Members")
			timeoutRole=discord.utils.get(guild.roles,name="Timeout")

			# Disallow unverified members
			if(memberRole not in guildMember.roles):
				await message.author.dm_channel.send( f"Sorry, to use the anonymous chat system, you need to at least have the role \"Members\" in the community's Discord server. You currently have the role \"{guildMember.top_role.name}\".", delete_after = 10 )
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
			username = random.choice( settings.anonymousNames )
			randomAvatarHash = random.choice( settings.anonymous.avatars )
			avatar = f"https://discordapp.com/assets/{ randomAvatarHash }.png"

			# A placeholder list for all the discord file objects
			files = []

			# Loop through all attachments that the user uploads
			for attachment in message.attachments:

				# Download the attachment
				path = downloadWebMedia( attachment.url )

				# Skip if the attachment wasn't downloaded
				if path == None: continue

				# Get the file extension
				_, extension = os.path.splitext( path )

				# Create an identical discord file object and append it to the files list
				files.append( discord.File( path, filename = "unknown" + extension, spoiler = attachment.is_spoiler() ) )

			# What to do after sending a message
			async def afterSentAnonMessage( anonMessage, directMessage ):

				# Calculate the message identifier and real deletion token
				messageIdentifier, deletionToken = anonymousMessageHashes( anonMessage, directMessage )

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

		# Fetch the #greetings channel
		greetingsChannel = client.get_channel( settings.channels.greetings )

		# Log this member join event
		await log( "Member joined", member.mention + " joined the server.", thumbnail = member.avatar_url )

		# Query the date & time that the member joined from the database
		results = mysqlQuery( "SELECT Joined, Steam FROM Members WHERE Member = LOWER( HEX( AES_ENCRYPT( '" + str( member.id ) + "', UNHEX( SHA2( '" + secrets.encryptionKeys.members + "', 512 ) ) ) ) );" )

		# Have they been in the server before? (we got results from the database)
		if len( results ) > 0:

			# Set their year role to whatever joined at date & time was in the database
			yearJoined = results[ 0 ][ 0 ].year

			# Is the steam community ID column not null (i.e. are they verified)?
			if results[ 0 ][ 1 ]:

				# Fetch the members role
				membersRole = member.guild.get_role( settings.roles.members )

				# Give the member that year role and the members role
				await member.add_roles( membersRole, reason = "Member is already verified." )

			# Send a welcome back message to the #greetings channel
			await greetingsChannel.send( ":wave::skin-tone-1: Welcome back " + member.mention + ", it's great to see you here again!", allowed_mentions = ALLOW_USER_MENTIONS )

		# This is their first time joining (we didn't get any results from the database)
		else:

			# Add the member to the database
			mysqlQuery( "INSERT INTO Members ( Member, Joined ) VALUES ( LOWER( HEX( AES_ENCRYPT( '" + str( member.id ) + "', UNHEX( SHA2( '" + secrets.encryptionKeys.members + "', 512 ) ) ) ) ), '" + member.joined_at.strftime( "%Y-%m-%d %H:%M:%S" ) + "' );" )

			# Set their year role to when they joined (which should always be right now, unless Discord is taking a shit)
			yearJoined = member.joined_at.year

			# Send a first welcome message to the #greetings channel
			await greetingsChannel.send( ":wave::skin-tone-1: Welcome " + member.mention + " to the Conspiracy Servers community! <:ConspiracyServers:540654522650066944>\nPlease be sure to read through the rules, guidelines and information in <#" + str( settings.channels.welcome ) + ">.", allowed_mentions = ALLOW_USER_MENTIONS )

		# Fetch the role for the year we just set above
		yearRole = member.guild.get_role( settings.roles.years[ str( yearJoined ) ] )

		# Give the member that year role
		await member.add_roles( yearRole, reason = "Member joined the server." )

# Runs when a member leaves
async def on_member_remove(member):
	await client.wait_until_ready()

	newChannel=discord.utils.get(member.guild.text_channels,name="greetings")

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
		await newChannel.send(f":bangbang: {member} was kicked by {moderator.mention}" + (f" for {reason}" if (reason) else "") + ".")
		await log("Member kicked", f"{member} was kicked by {moderator.mention}" + (f" for `{reason}`" if (reason) else "") + ".", thumbnail=member.avatar_url)
	elif (event == 2):
		await newChannel.send(f":bangbang: {member} was banned by {moderator.mention}" + (f" for {reason}" if (reason) else "") + ".")
		await log("Member banned", f"{member} was banned by {moderator.mention}" + (f" for `{reason}`" if (reason) else "") + ".", thumbnail=member.avatar_url)
	else:
		await newChannel.send(f":walking::skin-tone-1: {member} left the server.")
		await log("Member left", f"{member} left the server.", thumbnail=member.avatar_url)

# Runs when a message is deleted
async def on_message_delete(message):

	# Don't run if this is a Direct Message
	if message.guild == None: return

	if (not isValid(message)): return

	# Prevent further execution if this event shouldn't be logged
	if not shouldLog( message ): return

	# This for some reason doesn't work?
	after = datetime.datetime.now()-datetime.timedelta(seconds=10)
	moderator = None
	async for entry in message.guild.audit_logs(limit=1, action=discord.AuditLogAction.message_delete):
		if (entry.created_at > after) and (entry.target.id == message.author.id):
			moderator = entry.user
			break

	if (len(message.attachments) >= 1):
		for attachment in message.attachments:
			if (attachment.width) and (attachment.height):
				await log("Image deleted", f"Image [{attachment.filename} ({attachment.width}x{attachment.height}) ({hurry.filesize.size(attachment.size, system=hurry.filesize.alternative)})]({attachment.proxy_url}) uploaded by {message.author.mention} in {message.channel.mention} was deleted" + (f" by {moderator.mention}" if (moderator) else "") + ".", image=attachment.proxy_url)
			else:
				await log("Upload deleted", f"Upload [{attachment.filename} ({hurry.filesize.size(attachment.size, system=hurry.filesize.alternative)})]({attachment.url}) uploaded by {message.author.mention} in {message.channel.mention} was deleted" + (f" by {moderator.mention}" if (moderator) else "") + ".")
			
	if (message.clean_content != ""):
		await log("Message deleted", f"`{message.content}` sent by {message.author.mention} in {message.channel.mention} was deleted" + (f" by {moderator.mention}" if (moderator) else "") + ".")

# Runs when a message is edited
async def on_message_edit(originalMessage, editedMessage):

	# Don't run if this is a Direct Message
	if originalMessage.guild == None: return

	if (not isValid(originalMessage)) or (originalMessage.clean_content == editedMessage.clean_content): return

	# Increment the message edit statistic for this member
	mysqlQuery( "UPDATE MemberStatistics SET Edits = Edits + 1 WHERE Member = LOWER( HEX( AES_ENCRYPT( '" + str( originalMessage.author.id ) + "', UNHEX( SHA2( '" + secrets.encryptionKeys.memberStatistics + "', 512 ) ) ) ) );" )

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

# Runs when the client is ready
async def on_ready():

	# Bring some global variables into this scope
	global randomActivityTask, updateCategoryTask

	# Register the rest of the callbacks
	client.event( on_message )
	client.event( on_message_edit )
	client.event( on_message_delete )
	client.event( on_member_join )
	client.event( on_member_remove )
	client.event( on_reaction_add )
	client.event( on_reaction_remove )
	print( "Registered callbacks." )

	# Launch background tasks - keep this the same as on_resumed
	randomActivityTask = client.loop.create_task( chooseRandomActivity() )
	updateCategoryTask = client.loop.create_task( updateCategoryStatus() )
	print( "Launched background tasks." )

	# Console message
	print( "Ready." )

# Be safe!
try:

	# Register a few initial callbacks
	client.event( on_connect )
	client.event( on_resumed )
	client.event( on_disconnect )
	client.event( on_ready )

	# Start the client
	client.loop.run_until_complete( client.start( secrets.token ) )

# Catch keyboard interrupts
except KeyboardInterrupt:

	# Console message
	print( "Shutting down..." )

	# Close the client
	client.loop.run_until_complete( client.close() )

	# Close the event loop
	client.loop.close()

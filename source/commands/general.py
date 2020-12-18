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
from __main__ import chatCommands, settings, fileChecksum

# Import required modules
import discord, youtube_dl

# debbuggin'
from pprint import pprint

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

# The function to be called for download progress reporting for the chat command below
async def downloadCallback( event, message, arguments ):

	# It has finished downloading
	if event[ "status" ] == "finished":
		
		# Console message
		print( "Downloaded: " + event[ "filename" ] + " (" + "{:,}".format( event[ "total_bytes" ] ) + "b) (" + ( str( round( event[ "elapsed" ], 2 ) ) + "s elapsed" if "elapsed" in event else "located" ) + ")" )

		# The path to the file excluding web document root
		webPath = event[ "filename" ].replace( "/srv/www/conspiracyservers.com/files.conspiracyservers.com/downloads/", "" )

		# Friendly message
		await message.channel.send( "https://content.conspiracyservers.com/" + webPath )

	# The download is in progress
	elif event[ "status" ] == "downloading":

		# Console message
		print( "Downloading: " + event[ "filename" ] + " (" + "{:,}".format( event[ "downloaded_bytes" ] ) + "/" + "{:,}".format( event[ "total_bytes" ] ) + "b, " + "{:,}".format( round( event[ "speed" ] ) ) + "b/s, " + str( round( ( event[ "downloaded_bytes" ] / event[ "total_bytes" ] ) * 100, 2 ) ) + "%) (" + str( round( event[ "elapsed" ], 2 ) ) + "s elapsed)" )

	# Some other status
	else:
		print( "" )
		pprint( event )
		print( "" )

# Download an online video
@chatCommands( category = "General", aliases = [ "dl" ], wip = True )
async def download( message, arguments, client ):

	# Send a message if no arguments were provided
	if len( arguments ) < 1: return { "content": ":grey_exclamation: You must specify a link to a video, image, or other type of media." }

	# Set the download options
	options = {
		"quiet": True,
		"format": "best",
		"restrictfilenames": True,
		"nooverwrites": True,
		"outtmpl": "/var/www/conspiracyservers.com/files/downloads/%(extractor)s/%(id)s.%(ext)s",
		"progress_hooks": [
			lambda event: client.loop.create_task( downloadCallback( event, message, arguments ) )
		]
	}

	# Download it
	with youtube_dl.YoutubeDL( options ) as ytdl: ytdl.download( arguments )

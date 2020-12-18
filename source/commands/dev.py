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
from __main__ import chatCommands

# Import required modules
import discord, asyncio, time

##############################################
# Define chat commands
##############################################

# Sleep
@chatCommands( category = "Dev", wip = True )
async def sleep( message, arguments, client ):

	# Send a message if no arguments were provided
	if len( arguments ) < 1: return { "content": ":grey_exclamation: You must specify the duration to sleep for in seconds." }

	# Convert the duration argument to a float
	duration = float( arguments[ 0 ] )

	# Friendly message
	await message.channel.send( "Sleeping for `" + "{0:.16f}".format( duration ) + "` seconds..." )

	# Store high resolution time in seconds of when the sleeping started
	started = time.perf_counter()

	# Sleep
	await asyncio.sleep( duration )

	# Store high resolution time in seconds of when the sleeping finished
	finished = time.perf_counter() - started

	# Friendly message
	await message.channel.send( "Finished sleeping, sleep lasted exactly `" + "{0:.16f}".format( finished ) + "` seconds." )

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
@chatCommands( category = "Dev", aliases = [ "dl" ], wip = True )
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

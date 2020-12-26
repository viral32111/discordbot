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

##############################################
# Define chat commands
##############################################

# Add/remove a member from the Music DJ role
@chatCommands( category = "Music", aliases = [ "dj" ] )
async def toggledj( message, arguments, client ):

	# Get the DJ role
	musicDJ = message.guild.get_role( 784532835348381776 )

	# Get the Music voice channel
	musicChannel = message.guild.get_channel( 257480146762596352 )

	# Send a message if the caller is not a Music DJ
	if musicDJ not in message.author.roles: return { "content": ":no_entry_sign: This command can only be used by a " + musicDJ.mention + "." }

	# Send a message if no arguments were provided
	if len( message.mentions ) < 1: return { "content": ":grey_exclamation: You must mention the member(s) to toggle " + musicDJ.mention + " on." }

	# Loop through each mentioned member
	for member in message.mentions:

		# Is the member not in the Music voice channel?
		if member not in musicChannel.members:

			# Send a message
			await message.channel.send( member.mention + " needs to be in the Music voice channel." )

			# Skip to the next member
			continue

		# Does the member already have the Music DJ role?
		if musicDJ in member.roles:

			# Remove the role from them
			await member.remove_roles( musicDJ, reason = "Member was removed from Music DJ by " + str( message.author ) + "." )

			# Send a message
			await message.channel.send( ":white_check_mark: " + member.mention + " is no longer a " + musicDJ.mention + "." )

		# They do not have the Music DJ role
		else:

			# Add the role to them
			await member.add_roles( musicDJ, reason = "Member was added to Music DJ added by " + str( message.author ) + "." )

			# Send a message
			await message.channel.send( ":white_check_mark: " + member.mention + " is now a " + musicDJ.mention + "." )

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

# Shutdown the bot
@chatCommands( category = "Dev", aliases = [ "restart" ], wip = True )
async def shutdown( message, arguments, client ):

	# Log the event
	await log( "Bot shutdown", "The bot was shutdown by " + message.author.mention )

	# Delete the shutdown message
	await message.delete()

	###### EVENTUALLY REPLACE CODE BELOW WITH A CALL TO shutdown() AT THE BOTTOM OF THIS FILE

	# Console message
	print( "Shutting down..." )

	# Cancel all background tasks
	for backgroundTask in backgroundTasks: backgroundTask.cancel()

	# Remove all background tasks from the list
	backgroundTasks.clear()

	# Make the bot look offline while the connection times out
	await client.change_presence( status = discord.Status.offline )

	# Logout & disconnect
	await client.logout()

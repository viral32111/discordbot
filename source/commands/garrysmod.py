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
from __main__ import chatCommands, latestServerStatus, updateLocalServerStatus, updateServerCategoryStatusWithLocal, Server

# Import required modules
import discord

##############################################
# Define chat commands
##############################################

# Sandbox server status
@chatCommands( category = "Garry's Mod", aliases = [ "sbox" ] )
async def sandbox( message, arguments, client ):

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
			icon_url = "https://content.conspiracyservers.com/icons/hammer.png"
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

	# Update the category status too
	await updateServerCategoryStatusWithLocal( "sandbox" )

	# Send the embed
	return { "embed": embed }
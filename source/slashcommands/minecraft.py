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
from __main__ import slashCommands, InteractionResponse, InteractionResponseType, InteractionApplicationCommandCallbackData, ApplicationCommandOption, ApplicationCommandOptionType

# Import required modules
import discord, mcstatus, socket, re

##############################################
# Define slash commands
##############################################

# Minecraft
@slashCommands( early = True, description = "Interact with viral32111's Minecraft server.", options = [
	ApplicationCommandOption(
		type = ApplicationCommandOptionType.SubCommand,
		name = "status",
		description = "A brief real-time status of the Minecraft server."
	)
] )
async def minecraft( client, guild, channel, member, options ):
	server = mcstatus.MinecraftServer( "viral32111.com", 25565 )
	embed = discord.Embed( title = "", description = "Nothing is known about the server at this time. Try again later.", color = 0xf7894a )
	embed.set_author( name = "viral32111's minecraft server", icon_url = "https://viral32111.com/images/minecraft/brick.png" )
	embed.set_footer( text = f"Requested by { member.name }#{ member.discriminator }." )

	try:
		latency = server.ping()
		query = server.query()
	except socket.timeout:
		embed.description = "Timed out while fetching information! The server is likely offline at the moment."
	else:
		embed.description = ""
		embed.add_field( name = "__Status__", value = f"• Players: { query.players.online } / { query.players.max }\n• Latency: { round( latency ) }ms\n• Version: { query.software.version }\n• Software: { query.software.brand }", inline = False )

		if query.players.online > 0:
			playerText = ""
			for player in query.players.names:
				playerText += f"• { player }"
				#print( player )
				#match = re.match( r"^(.+) \(([\w\d-]+)\)$", player )
				#playerText += f"• [{ match.group( 1 ) }](https://namemc.com/profile/{ match.group( 2 ) })"
			embed.add_field( name = "__Players__", value = playerText, inline = False )

	return InteractionResponse(
		InteractionResponseType.ChannelMessage,
		InteractionApplicationCommandCallbackData(
			"",
			embeds = [ embed ]
		)
	)

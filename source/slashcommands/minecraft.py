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
from __main__ import slashCommands, InteractionResponse, InteractionResponseType, InteractionApplicationCommandCallbackData, ApplicationCommandOption, ApplicationCommandOptionType, formatSeconds

# Import required modules
import discord, mcstatus, socket, re, json, requests, requests_unixsocket, datetime, dateutil.parser

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
async def minecraft( client, guild, channel, member, options, early ):
	if early == True:
		embed = discord.Embed( title = "", description = "Fetching server information...", color = 0xf7894a )
		embed.set_footer( text = f"Requested by { member.name }#{ member.discriminator }." )
		embed.set_author( name = "viral32111's minecraft server", icon_url = "https://viral32111.com/images/minecraft/brick.png" )
		return InteractionResponse(
			InteractionResponseType.ChannelMessage,
			InteractionApplicationCommandCallbackData(
				"",
				embeds = [ embed ]
			)
		)

	server = mcstatus.MinecraftServer( "viral32111.com", 25565 )
	embed = discord.Embed( title = "", description = "Nothing is known about the server at this time. Try again later.", color = 0xf7894a )
	embed.set_author( name = "viral32111's minecraft server", icon_url = "https://viral32111.com/images/minecraft/brick.png" )
	embed.set_footer( text = f"Requested by { member.name }#{ member.discriminator }." )

	try:
		query = server.query()

		with open( "/srv/minecraft/usercache.json", "r" ) as theFile:
			playerCache = json.loads( theFile.read() )
			playerLookup = { player[ "name" ]: player[ "uuid" ] for player in playerCache }

		with open( "/srv/minecraft/minecraft.cid", "r" ) as theFile:
			containerID = theFile.read()
		
			with requests_unixsocket.monkeypatch():
				inspectRequest = requests.get( f"http+unix://%2Fvar%2Frun%2Fdocker.sock/containers/{ containerID }/json" ).json()
				statsRequest = requests.get( f"http+unix://%2Fvar%2Frun%2Fdocker.sock/containers/{ containerID }/stats?stream=false" ).json()

				containerUptime = datetime.datetime.now() - dateutil.parser.parse( inspectRequest[ "Created" ] ).replace( tzinfo = None )
				cpuUsage = round( ( ( statsRequest[ "cpu_stats" ][ "cpu_usage" ][ "total_usage" ] - statsRequest[ "precpu_stats" ][ "cpu_usage" ][ "total_usage" ] ) / ( statsRequest[ "cpu_stats" ][ "system_cpu_usage" ] - statsRequest[ "precpu_stats" ][ "system_cpu_usage" ] ) ) * statsRequest[ "cpu_stats" ][ "online_cpus" ] * 100.0, 2 )
				memoryUsage = round( ( ( statsRequest[ "memory_stats" ][ "usage" ] - statsRequest[ "memory_stats" ][ "stats" ][ "cache" ] ) / statsRequest[ "memory_stats" ][ "limit" ] ) * 100.0, 2 )
	except socket.timeout:
		embed.description = "Timed out while fetching information! The server is likely offline at the moment."
	else:
		embed.description = ""
		embed.add_field( name = "__Status__", value = f"• Players: { query.players.online } / { query.players.max }\n• Uptime: { formatSeconds( int( containerUptime.total_seconds() ) ) }\n• Version: { query.software.version }\n• Software: { query.software.brand }", inline = False )
		embed.add_field( name = "__Resources__", value = f"• Processor: { cpuUsage }%\n• Memory: { memoryUsage }%", inline = False )

		if query.players.online > 0:
			playerText = ""
			for player in query.players.names:
				uuid = playerLookup[ player ]
				playerText += f"• [{ discord.utils.escape_markdown( player ) }](https://namemc.com/profile/{ uuid })\n"
			embed.add_field( name = "__Players__", value = playerText, inline = False )

	return InteractionResponse(
		InteractionResponseType.ChannelMessage,
		InteractionApplicationCommandCallbackData(
			"",
			embeds = [ embed ]
		)
	)

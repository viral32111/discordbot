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
from __main__ import formatSeconds

# Import required modules
import discord, mcstatus, socket, requests, requests_unixsocket, datetime, dateutil.parser, os, slashcommands

##############################################
# Define slash commands
##############################################

# Minecraft Status
@slashcommands.new( "The current status of the Minecraft server." )
async def minecraft( interaction ):
	message = await interaction.think()

	embed = discord.Embed( title = "", description = "", color = 0xF7894A )
	embed.set_author( name = "viral32111's minecraft server", icon_url = "https://viral32111.com/images/minecraft/brick.png" )

	try:
		server = mcstatus.MinecraftServer( "viral32111.com" )
		status = server.status()
		query = server.query()

		with requests_unixsocket.monkeypatch():
			inspectRequest = requests.get( f"http+unix://%2Fvar%2Frun%2Fdocker.sock/containers/minecraft/json" ).json()
			statsRequest = requests.get( f"http+unix://%2Fvar%2Frun%2Fdocker.sock/containers/minecraft/stats?stream=false" ).json()

			containerUptime = datetime.datetime.now() - dateutil.parser.parse( inspectRequest[ "Created" ] ).replace( tzinfo = None )
			cpuUsage = round( ( ( statsRequest[ "cpu_stats" ][ "cpu_usage" ][ "total_usage" ] - statsRequest[ "precpu_stats" ][ "cpu_usage" ][ "total_usage" ] ) / ( statsRequest[ "cpu_stats" ][ "system_cpu_usage" ] - statsRequest[ "precpu_stats" ][ "system_cpu_usage" ] ) ) * statsRequest[ "cpu_stats" ][ "online_cpus" ] * 100.0, 2 )
			memoryUsage = round( ( ( statsRequest[ "memory_stats" ][ "usage" ] - statsRequest[ "memory_stats" ][ "stats" ][ "cache" ] ) / statsRequest[ "memory_stats" ][ "limit" ] ) * 100.0, 2 )
	except socket.timeout:
		embed.description = "Timed out while fetching information! The server is likely offline at the moment."
	else:
		embed.add_field( name = "__Status__", value = f"• Players: { status.players.online } / { status.players.max }\n• Uptime: { formatSeconds( int( containerUptime.total_seconds() ) ) }\n• Version: { query.software.version }\n• Software: { query.software.brand }", inline = False )
		embed.add_field( name = "__Resources__", value = f"• Processor: { cpuUsage }%\n• Memory: { memoryUsage }%", inline = False )

		if status.players.online > 0:
			playerText = "\n".join( [ f"• [{ discord.utils.escape_markdown( player.name ) }](https://namemc.com/profile/{ player.id })" for player in status.players.sample ] )
			embed.add_field( name = "__Players__", value = playerText, inline = False )

	await message.edit( embeds = [ embed ] )

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
from __main__ import log, backgroundTasks

# Import required modules
import slashcommands, discord

##############################################
# Define slash commands
##############################################

# Shutdown
@slashcommands.new( "Gracefully shuts down the bot, only for viral32111 :).", guild = 240167618575728644 )
async def shutdown( interaction ):

	if interaction.user.id != interaction.client.guilds[ 0 ].owner_id:
		await interaction.respond( "This isn't for you!", hidden = True )
		return

	print( "Shutting down..." )

	await interaction.respond( "Shutting down...", hidden = True )

	await log( "Bot shutdown", "The bot was shutdown by <@" + str( interaction.user.id ) + ">" )

	for backgroundTask in backgroundTasks: backgroundTask.cancel()
	backgroundTasks.clear()

	await interaction.client.change_presence( status = discord.Status.offline )

	await interaction.client.close()

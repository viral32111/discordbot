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
from __main__ import slashCommands, InteractionResponse, InteractionResponseType, InteractionApplicationCommandCallbackData

# Import required modules
import discord

##############################################
# Define slash commands
##############################################

# Hello
@slashCommands( description = "A simple test command to check everything works." )
async def hello( guild, channel, member, options ):
	return InteractionResponse(
		InteractionResponseType.ChannelMessageWithSource,
		InteractionApplicationCommandCallbackData(
			f"Hello { member.mention }!"
		)
	)

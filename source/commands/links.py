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
from __main__ import chatCommands

# Import required modules
import discord

##############################################
# Define chat commands
##############################################

# Website
@chatCommands( category = "Links", aliases = [ "site" ] )
async def website( message, arguments, client ):

	# Respond with a simple message
	return { "content": ":link: The community website is available at https://viral32111.com/community" }

# Steam Group
@chatCommands( category = "Links", aliases = [ "steam" ] )
async def steamgroup( message, arguments, client ):

	# Respond with a simple message
	return { "content": ":link: The community Steam Group is available at https://viral32111.com/steam" }

# Discord
@chatCommands( category = "Links", aliases = [ "invite" ] )
async def discord( message, arguments, client ):

	# Respond with a simple message
	return { "content": ":link: The community Discord invite link is https://viral32111.com/discord" }

# Staff Application
@chatCommands( category = "Links", aliases = [ "apply" ] )
async def staffapplication( message, arguments, client ):

	# Respond with a simple message
	return { "content": ":link: You can apply for Staff by filling out the application available at https://viral32111.com/apply" }

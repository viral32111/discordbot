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
from __main__ import chatCommands, settings

# Import required modules
import discord

##############################################
# Define chat commands
##############################################

# Timeout a user
@chatCommands( category = "Moderation" )
async def timeout( message, arguments, client ):

	# Does the user not have the manage messages permission?
	if not message.author.guild_permissions.manage_messages:

		# Feedback message
		return { "content": ":no_entry_sign: This command can only be used by staff members." }

	# Was there no mentions?
	if len( message.mentions ) < 1:

		# Friendly message
		return { "content": ":grey_exclamation: You must mention at least one member." }

	# Fetch the timeout role
	timeoutRole = message.channel.guild.get_role( settings.roles.timeout )

	# Loop through every mentioned member
	for member in message.mentions:

		# Give the member the timeout role
		await member.add_roles( timeoutRole, reason = "Member timed out by " + str( message.author ) )
	
		# Send message feedback
		await message.channel.send( "Timed out " + member.mention + " indefinitely." )

# Remove a user from timeout
@chatCommands( category = "Moderation" )
async def untimeout( message, arguments, client ):

	# Does the user not have the manage messages permission?
	if not message.author.guild_permissions.manage_messages:

		# Feedback message
		return { "content": ":no_entry_sign: This command can only be used by staff members." }

	# Was there no mentions?
	if len( message.mentions ) < 1:

		# Friendly message
		return { "content": ":grey_exclamation: You must mention at least one member." }

	# Fetch the timeout role
	timeoutRole = message.channel.guild.get_role( settings.roles.timeout )

	# Loop through every mentioned member
	for member in message.mentions:

		# Are they using it on themselves?
		if member.id == message.author.id:
			
			# Friendly message
			await message.channel.send( ":no_entry_sign: You cannot remove yourself from timeout." )

			# Prevent further execution
			return

		# Remove the timeout role from the member
		await member.remove_roles( timeoutRole, reason = "Member removed from timeout by " + str( message.author ) )
	
		# Send message feedback
		await message.channel.send( "Removed " + member.mention + " from timeout." )
